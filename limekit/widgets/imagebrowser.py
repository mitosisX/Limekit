"""A project's images, kept in folders: browse, import, move, rename, delete.

The folder on disk is the only truth. Both views sit on QFileSystemModel,
which watches the folders it has loaded, so a file added from Explorer or
Finder shows up without a refresh. The browser does the file operations
itself -- copy in, move between folders, rename, send to the trash -- and
reports that something changed; what a change *means* (regenerating a
module of image names, say) is the caller's business.

Names are kept unique across the whole tree, not just per folder. A caller
that refers to images by name -- `images.logo` rather than a path -- can
then move a file between folders without anything that names it breaking.
"""

import os
import shutil

from PySide6.QtCore import QDir, QFileInfo, QMimeData, QSize, Qt, QTimer, QUrl
from PySide6.QtGui import QDrag, QIcon
from PySide6.QtWidgets import (QAbstractItemView, QFileIconProvider,
                               QFileSystemModel, QHBoxLayout, QInputDialog,
                               QLabel, QListView, QMessageBox, QSplitter,
                               QStyle, QToolButton, QTreeView, QVBoxLayout,
                               QWidget, QFileDialog)

from limekit.kernel.bridge.guard import guard
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import method
from limekit.widgets.base import LimeWidget

#: A drag of one of the browser's images. Payload: its path relative to the
#: browser's root, with forward slashes. File URLs ride along too, so an
#: image can be dragged out to anywhere that takes files.
IMAGE_MIME = "application/x-limekit-image"

IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".ico", ".webp")


def is_image(path):
    return os.path.splitext(str(path))[1].lower() in IMAGE_SUFFIXES


def name_key(stem):
    """The identifier an image is known by: letters, digits and underscores,
    not starting with a digit. "my-logo@2x" -> "my_logo_2x"."""
    key = "".join(c if c.isalnum() or c == "_" else "_" for c in stem).strip("_") or "image"
    while "__" in key:
        key = key.replace("__", "_")
    return ("_" + key) if key[0].isdigit() else key


def _stems_under(root, except_path=None):
    taken = set()
    for folder, _dirs, files in os.walk(root):
        for f in files:
            full = os.path.join(folder, f)
            if is_image(f) and (except_path is None or os.path.normcase(full) != os.path.normcase(except_path)):
                taken.add(name_key(os.path.splitext(f)[0]).lower())
    return taken


def unique_target(root, folder, filename, except_path=None):
    """A path in `folder` for `filename` whose name is unused anywhere under
    `root` -- "logo.png", else "logo_2.png", "logo_3.png"..."""
    stem, ext = os.path.splitext(filename)
    taken = _stems_under(root, except_path)
    candidate, n = stem, 2
    while name_key(candidate).lower() in taken or os.path.exists(os.path.join(folder, candidate + ext)):
        candidate, n = f"{stem}_{n}", n + 1
    return os.path.join(folder, candidate + ext)


class _Thumbnails(QFileIconProvider):
    """Images show themselves; everything else gets the platform's icon."""

    def icon(self, what):
        if isinstance(what, QFileInfo) and what.isFile() and is_image(what.fileName()):
            icon = QIcon(what.absoluteFilePath())
            if not icon.isNull():
                return icon
        return super().icon(what)


class _DropTarget:
    """Shared by both views: accept local image files, and say where they go."""

    def _browser(self):
        return self.parent_browser

    def dragEnterEvent(self, event):
        if self._browser()._droppable(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if self._browser()._droppable(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        folder = self._drop_folder(event.position().toPoint())
        if self._browser()._take(event.mimeData(), folder):
            event.acceptProposedAction()
        else:
            event.ignore()


class _FolderTree(_DropTarget, QTreeView):
    def __init__(self, browser):
        super().__init__()
        self.parent_browser = browser
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def _drop_folder(self, point):
        index = self.indexAt(point)
        if index.isValid():
            return self.model().filePath(index)
        return self._browser()._root


class _ImageGrid(_DropTarget, QListView):
    def __init__(self, browser):
        super().__init__()
        self.parent_browser = browser
        self.setAcceptDrops(True)
        self.setDragEnabled(True)

    def _drop_folder(self, point):
        return self._browser().currentFolderPath()

    def startDrag(self, actions):
        index = self.currentIndex()
        if not index.isValid():
            return
        path = self.model().filePath(index)
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(path)])
        mime.setData(IMAGE_MIME, self._browser().relative(path).encode())
        drag = QDrag(self)
        drag.setMimeData(mime)
        icon = self.model().fileIcon(index)
        if not icon.isNull():
            drag.setPixmap(icon.pixmap(48, 48))
        drag.exec(Qt.DropAction.MoveAction | Qt.DropAction.CopyAction)


class ImageBrowser(LimeWidget, QWidget):
    __lime__ = "ui.ImageBrowser"

    def __init__(self):
        super().__init__()
        self._root = None
        self._current = None
        self._onChange = None
        self._onPick = None
        self._onSelect = None

        self._folders = QFileSystemModel(self)
        self._folders.setFilter(QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot)
        self._files = QFileSystemModel(self)
        self._files.setFilter(QDir.Filter.Files)
        self._files.setNameFilters(["*" + s for s in IMAGE_SUFFIXES])
        self._files.setNameFilterDisables(False)
        self._files.setIconProvider(_Thumbnails())

        self.tree = _FolderTree(self)
        self.tree.setModel(self._folders)
        for column in range(1, 4):
            self.tree.hideColumn(column)
        self.tree.setHeaderHidden(True)
        self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.grid = _ImageGrid(self)
        self.grid.setModel(self._files)
        self.grid.setViewMode(QListView.ViewMode.IconMode)
        self.grid.setIconSize(QSize(48, 48))
        self.grid.setGridSize(QSize(92, 86))
        self.grid.setResizeMode(QListView.ResizeMode.Adjust)
        self.grid.setMovement(QListView.Movement.Static)
        self.grid.setWordWrap(True)
        self.grid.setUniformItemSizes(True)
        self.grid.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # A breadcrumb: each folder on the way down is a link back up.
        self.where = QLabel()
        self.where.setTextFormat(Qt.TextFormat.RichText)
        self.where.linkActivated.connect(self._crumb)
        self.info = QLabel()
        self.info.setWordWrap(True)
        self.info.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        bar = QHBoxLayout()
        bar.setContentsMargins(0, 0, 0, 0)
        self._buttons = []
        style = self.style()
        for text, tip, icon, slot in (
                ("New folder", "Make a folder inside the one shown",
                 QStyle.StandardPixmap.SP_FileDialogNewFolder, self._new_folder),
                ("Import...", "Copy image files into the folder shown",
                 QStyle.StandardPixmap.SP_DialogOpenButton, self._import),
                ("Rename", "Rename the selected image or folder",
                 QStyle.StandardPixmap.SP_FileDialogDetailedView, self._rename),
                ("Delete", "Move the selected image or folder to the trash",
                 QStyle.StandardPixmap.SP_TrashIcon, self._delete)):
            button = QToolButton()
            button.setText(text)
            button.setToolTip(tip)
            button.setIcon(style.standardIcon(icon))
            button.setAutoRaise(True)
            button.clicked.connect(slot)
            bar.addWidget(button)
            self._buttons.append(button)
        bar.addStretch(1)

        self.split = QSplitter(Qt.Orientation.Vertical)
        self.split.addWidget(self.tree)
        self.split.addWidget(self.grid)
        self.split.setStretchFactor(0, 1)
        self.split.setStretchFactor(1, 3)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(bar)
        layout.addWidget(self.where)
        layout.addWidget(self.split, 1)
        layout.addWidget(self.info)

        # Many signals for one user action (a move is a removal and an
        # insertion, in two models): gather them into one onChange.
        self._settle = QTimer(self)
        self._settle.setSingleShot(True)
        self._settle.setInterval(250)
        self._settle.timeout.connect(self._emit_change)
        for model in (self._folders, self._files):
            model.rowsInserted.connect(self._changed)
            model.rowsRemoved.connect(self._changed)
            model.fileRenamed.connect(self._changed)

        self.tree.selectionModel().currentChanged.connect(self._folder_chosen)
        self.grid.selectionModel().currentChanged.connect(self._image_chosen)
        self.grid.doubleClicked.connect(self._image_picked)
        self.setOrientation("vertical")

    # -- the root and the current folder ----------------------------------

    @method({"path": "string"}, returns="self",
            doc="The folder whose images are managed -- usually a project's "
                "images folder. Made if it does not exist.")
    def setRoot(self, path):
        path = os.path.normpath(str(path))
        os.makedirs(path, exist_ok=True)
        self._root = path
        self._folders.setRootPath(path)
        self.tree.setRootIndex(self._folders.index(path))
        self._show_folder(path)
        return self

    @method(returns="string", doc="The managed folder, or nil.")
    def getRoot(self):
        return self._root

    def currentFolderPath(self):
        return self._current or self._root

    @method(returns="string", doc="The folder being shown, relative to the root ('' for the root).")
    def getCurrentFolder(self):
        return self.relative(self.currentFolderPath()) if self._root else ""

    def relative(self, path):
        rel = os.path.relpath(path, self._root)
        return "" if rel == "." else rel.replace(os.sep, "/")

    def _inside(self, path):
        root = os.path.normcase(os.path.abspath(self._root))
        path = os.path.normcase(os.path.abspath(path))
        return path == root or path.startswith(root + os.sep)

    def _show_folder(self, path):
        self._current = path
        self._files.setRootPath(path)
        self.grid.setRootIndex(self._files.index(path))
        rel = self.relative(path)
        crumbs, walked = ['<a href="/">images</a>'], []
        for part in [p for p in rel.split("/") if p]:
            walked.append(part)
            crumbs.append(f'<a href="{"/".join(walked)}">{part}</a>')
        self.where.setText(" / ".join(crumbs))
        self.info.setText("Drop image files here, or onto a folder.")

    def _folder_chosen(self, current, _previous):
        if current.isValid():
            self._show_folder(self._folders.filePath(current))

    @method({"orientation": '"vertical"|"horizontal"'}, returns="self",
            doc="Folders above the images (vertical, for a narrow panel) or "
                "beside them (horizontal).")
    def setOrientation(self, orientation):
        wide = str(orientation) == "horizontal"
        self.split.setOrientation(Qt.Orientation.Horizontal if wide else Qt.Orientation.Vertical)
        # In a narrow panel the buttons' words do not fit; the icons do,
        # and the tooltips still say what each one is.
        for button in self._buttons:
            button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon if wide
                                      else Qt.ToolButtonStyle.ToolButtonIconOnly)
        return self

    def _crumb(self, rel):
        rel = str(rel).strip("/")
        path = os.path.join(self._root, *[p for p in rel.split("/") if p])
        if rel:
            self.tree.setCurrentIndex(self._folders.index(path))
        else:
            self.tree.clearSelection()
            self.tree.setCurrentIndex(self.tree.rootIndex())
        self._show_folder(path)

    @method({"text": "string"}, returns="self",
            doc="The line under the images -- e.g. how the selected image is "
                "referred to in code.")
    def setInfo(self, text):
        self.info.setText(str(text or ""))
        return self

    # -- selection --------------------------------------------------------

    @method(returns="string", doc="The selected image, relative to the root, or nil.")
    def getSelectedImage(self):
        index = self.grid.currentIndex()
        if not index.isValid():
            return None
        return self.relative(self._files.filePath(index))

    def _image_chosen(self, current, _previous):
        if self._onSelect is not None:
            self._onSelect(self.relative(self._files.filePath(current)) if current.isValid() else None)

    def _image_picked(self, index):
        if index.isValid() and self._onPick is not None:
            self._onPick(self.relative(self._files.filePath(index)))

    @method({"handler": "fun(image: string)"}, returns="self",
            doc="Called with an image's path relative to the root when it is selected, or nil.")
    def setOnSelect(self, handler):
        self._onSelect = guard(handler, widget="ImageBrowser", event="onSelect")
        return self

    @method({"handler": "fun(image: string)"}, returns="self",
            doc="Called with an image's path relative to the root when it is double-clicked.")
    def setOnPick(self, handler):
        self._onPick = guard(handler, widget="ImageBrowser", event="onPick")
        return self

    @method({"handler": "fun()"}, returns="self",
            doc="Called once after images or folders are added, moved, renamed "
                "or deleted -- here or, for folders being shown, outside.")
    def setOnChange(self, handler):
        self._onChange = guard(handler, widget="ImageBrowser", event="onChange")
        return self

    def _changed(self, *_):
        self._settle.start()

    def _emit_change(self):
        if self._onChange is not None:
            self._onChange()

    # -- bringing images in, and moving them ------------------------------

    def _droppable(self, mime):
        return self._root is not None and mime.hasUrls() and any(
            url.isLocalFile() and (is_image(url.toLocalFile()) or os.path.isdir(url.toLocalFile()))
            for url in mime.urls())

    def _take(self, mime, folder):
        """Copies image files in from outside, or moves them when they are
        already under the root. Returns whether anything happened."""
        if not self._droppable(mime) or not self._inside(folder):
            return False
        done = False
        for url in mime.urls():
            source = url.toLocalFile()
            if not url.isLocalFile() or not is_image(source) or not os.path.isfile(source):
                continue
            if self._inside(source):
                if os.path.normcase(os.path.dirname(os.path.abspath(source))) == os.path.normcase(os.path.abspath(folder)):
                    continue
                target = unique_target(self._root, folder, os.path.basename(source), except_path=source)
                shutil.move(source, target)
            else:
                target = unique_target(self._root, folder, os.path.basename(source))
                shutil.copy2(source, target)
            done = True
        if done:
            self._changed()
        return done

    @method({"paths": "string[]"}, returns="integer",
            doc="Copies image files into the folder being shown; returns how "
                "many came in. Names are made unique across the whole tree.")
    def importFiles(self, paths):
        from limekit.kernel.bridge.convert import as_sequence
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(str(p)) for p in as_sequence(paths)])
        before = sum(len(f) for _, _, f in os.walk(self._root))
        self._take(mime, self.currentFolderPath())
        return sum(len(f) for _, _, f in os.walk(self._root)) - before

    @method({"name": "string"}, returns="string",
            doc="Makes a folder inside the one being shown and returns its "
                "path relative to the root.")
    def newFolder(self, name):
        name = str(name).strip().strip("/\\")
        if not name or any(c in name for c in '<>:"/\\|?*'):
            raise BridgeError(f"not a usable folder name: {name!r}")
        path = os.path.join(self.currentFolderPath(), name)
        os.makedirs(path, exist_ok=True)
        self._changed()
        return self.relative(path)

    # -- the buttons --------------------------------------------------------

    def _selected_path(self):
        index = self.grid.currentIndex()
        if index.isValid() and self.grid.hasFocus():
            return self._files.filePath(index)
        folder = self.tree.currentIndex()
        if folder.isValid() and self.tree.hasFocus():
            return self._folders.filePath(folder)
        if index.isValid():
            return self._files.filePath(index)
        return None

    def _new_folder(self):
        if self._root is None:
            return
        name, ok = QInputDialog.getText(self, "New folder", "Folder name:")
        if ok and name.strip():
            try:
                self.newFolder(name)
            except BridgeError as error:
                QMessageBox.warning(self, "New folder", str(error))

    def _import(self):
        if self._root is None:
            return
        patterns = " ".join("*" + s for s in IMAGE_SUFFIXES)
        paths, _ = QFileDialog.getOpenFileNames(self, "Import images", "", f"Images ({patterns})")
        if paths:
            self.importFiles(paths)

    def _rename(self):
        path = self._selected_path()
        if path is None or os.path.normcase(path) == os.path.normcase(self._root):
            return
        folder, old = os.path.split(path)
        stem, ext = os.path.splitext(old) if os.path.isfile(path) else (old, "")
        name, ok = QInputDialog.getText(self, "Rename", "New name:", text=stem)
        name = name.strip()
        if not ok or not name or name == stem:
            return
        if os.path.isfile(path):
            if name_key(name).lower() in _stems_under(self._root, except_path=path):
                QMessageBox.warning(self, "Rename", f"An image called {name!r} already exists.")
                return
            os.replace(path, os.path.join(folder, name + ext))
        else:
            os.rename(path, os.path.join(folder, name))
        self._changed()

    def _delete(self):
        from PySide6.QtCore import QFile
        path = self._selected_path()
        if path is None or os.path.normcase(path) == os.path.normcase(self._root):
            return
        what = os.path.basename(path)
        answer = QMessageBox.question(self, "Delete", f"Move {what!r} to the trash?")
        if answer != QMessageBox.StandardButton.Yes:
            return
        # The trash, not os.remove: a deleted image is one undo away.
        if not QFile.moveToTrash(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        self._changed()

    @method(returns="self", doc="Re-reads the folders.")
    def refresh(self):
        if self._root is not None:
            self.setRoot(self._root)
        return self
