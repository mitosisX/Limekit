"""A list of every widget the designer can build, that can be dragged from.

Only classes `Introspect.buildableClasses()` reports are offered, and only
the ones that are widgets, so nothing in the list fails the moment it is
dropped. Grouping is a static table; a class added to Limekit without being
added here still appears, under "Other", rather than silently vanishing
from the palette.
"""

from PySide6.QtCore import QMimeData, QPoint, QRect, QSize, Qt
from PySide6.QtGui import QColor, QDrag, QFontMetrics, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (QLineEdit, QListWidget, QListWidgetItem,
                               QVBoxLayout, QWidget)

from limekit.kernel.bridge.convert import as_mapping, as_sequence, to_lua
from limekit.kernel.bridge.guard import guard
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import method
from limekit.widgets.base import LimeWidget
from limekit.widgets.designsurface import CLASS_MIME

_CLASS_ROLE = Qt.ItemDataRole.UserRole

GROUPS = (
    ("Containers", ("Container", "GroupBox", "Scroller", "Splitter", "Tab", "Accordion")),
    ("Inputs", ("Button", "CommandButton", "CheckBox", "RadioButton", "LineEdit",
                "TextField", "ComboBox", "FontComboBox", "Spinner", "DoubleSpinner",
                "Slider", "AdvancedSlider", "Knob", "DatePicker", "TimePicker",
                "Calendar")),
    ("Display", ("Label", "Image", "ProgressBar", "LCDNumber", "GifPlayer",
                 "HLine", "VLine", "Separator")),
    ("Data", ("ListBox", "Table", "TreeView", "TreeWidget")),
)

# Widgets that build, but are windows, chrome or designer machinery rather
# than something that goes inside a layout.
_NOT_ON_A_CANVAS = {
    "Window", "Modal", "Dock", "Dockable", "Menu", "Menubar", "DropMenu", "Toolbar", "StatusBar",
    "TabItem", "SlidingStackedWidget", "DesignSurface", "WidgetPalette", "ImageBrowser",
}


def palette_classes():
    """Widget classes worth offering, as "ui.Name" strings, sorted."""
    from limekit.kernel.registry import registry
    from limekit.services.inspect import buildable_classes

    classes = registry.modules().get("ui", {})
    out = []
    for name in buildable_classes():
        cls = classes.get(name)
        if cls is None or not issubclass(cls, QWidget) or name in _NOT_ON_A_CANVAS:
            continue
        out.append(f"ui.{name}")
    return sorted(out)


def grouped():
    """((title, [class, ...]), ...) in palette order, "Other" last."""
    remaining = set(palette_classes())
    out = []
    for title, names in GROUPS:
        members = [f"ui.{n}" for n in names if f"ui.{n}" in remaining]
        remaining -= set(members)
        if members:
            out.append((title, members))
    if remaining:
        out.append(("Other", sorted(remaining)))
    return tuple(out)


class _PaletteList(QListWidget):
    """A QListWidget whose drags carry a class name, not Qt's item model."""

    def mimeTypes(self):
        return [CLASS_MIME]

    def mimeData(self, items):
        mime = QMimeData()
        for item in items:
            cls = item.data(_CLASS_ROLE)
            if cls:
                mime.setData(CLASS_MIME, str(cls).encode())
                break
        return mime

    def startDrag(self, actions):
        """Drags a tag reading "+ Button" rather than Qt's default picture
        of the list row, so what is being carried onto the canvas is
        obvious the whole way there."""
        item = self.currentItem()
        if item is None or not item.data(_CLASS_ROLE):
            return
        drag = QDrag(self)
        drag.setMimeData(self.mimeData([item]))
        pixmap = _tag_pixmap(self, item.icon(), "+  " + item.text())
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(10, int(pixmap.deviceIndependentSize().height() / 2)))
        drag.exec(Qt.DropAction.CopyAction)


def _tag_pixmap(widget, icon, text):
    """A rounded accent tag with an icon and text, for dragging."""
    font = widget.font()
    font.setBold(True)
    metrics = QFontMetrics(font)
    dpr = widget.devicePixelRatioF()
    w, h = metrics.horizontalAdvance(text) + 40, metrics.height() + 12
    pixmap = QPixmap(int(w * dpr), int(h * dpr))
    pixmap.setDevicePixelRatio(dpr)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#2979FF"))
    painter.drawRoundedRect(QRect(0, 0, w, h), 6, 6)
    if not icon.isNull():
        # Drawn on a white chip so a dark line-art icon stays visible.
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawRoundedRect(QRect(5, (h - 20) // 2, 20, 20), 4, 4)
        icon.paint(painter, QRect(7, (h - 16) // 2, 16, 16))
    painter.setFont(font)
    painter.setPen(QColor("#FFFFFF"))
    painter.drawText(QRect(30, 0, w - 34, h), Qt.AlignmentFlag.AlignVCenter, text)
    painter.end()
    return pixmap


class WidgetPalette(LimeWidget, QWidget):
    __lime__ = "ui.WidgetPalette"

    def __init__(self):
        super().__init__()
        self._onPick = None

        self.filter = QLineEdit()
        self.filter.setPlaceholderText("Search widgets")
        self.filter.setClearButtonEnabled(True)

        self.list = _PaletteList()
        self.list.setIconSize(QSize(16, 16))
        self.list.setSpacing(1)
        self.list.setDragEnabled(True)
        self.list.setDragDropMode(QListWidget.DragDropMode.DragOnly)
        self.list.setDefaultDropAction(Qt.DropAction.CopyAction)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.filter)
        layout.addWidget(self.list)

        self._fill()
        self.filter.textChanged.connect(self._filter_changed)
        self.list.itemDoubleClicked.connect(self._pick)

    @staticmethod
    def _header(title):
        header = QListWidgetItem(title)
        # Enabled but not selectable: NoItemFlags would paint it in the
        # disabled colour, which is too faint to read as a heading.
        header.setFlags(Qt.ItemFlag.ItemIsEnabled)
        font = header.font()
        font.setBold(True)
        font.setPointSizeF(font.pointSizeF() * 0.85)
        font.setLetterSpacing(font.SpacingType.PercentageSpacing, 108)
        font.setCapitalization(font.Capitalization.AllUppercase)
        header.setFont(font)
        header.setSizeHint(QSize(0, 30))
        header.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        return header

    @staticmethod
    def _entry(text, payload, tip=None):
        item = QListWidgetItem(text)
        item.setData(_CLASS_ROLE, payload)
        if tip:
            item.setToolTip(tip)
        item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
                      | Qt.ItemFlag.ItemIsDragEnabled)
        return item

    def _fill(self):
        for title, classes in grouped():
            self.list.addItem(self._header(title))
            for cls in classes:
                self.list.addItem(self._entry(cls[3:], cls))

    @method({"title": "string", "entries": "table", "atTop": "boolean"}, returns="self",
            doc="Adds a group of entries that are not widget classes -- a "
                "layout, a ready-made arrangement. Each entry is {id = "
                "'layout:ui.HLayout', text = 'Row', tip = '...'}; the id is "
                "what a drop or a pick reports, exactly as a class would be. "
                "atTop puts the group before the widgets.")
    def addGroup(self, title, entries, atTop=False):
        items = [self._header(str(title))]
        for entry in as_sequence(entries):
            entry = as_mapping(entry)
            items.append(self._entry(str(entry.get("text") or entry["id"]),
                                     str(entry["id"]), entry.get("tip")))
        for offset, item in enumerate(items):
            if atTop:
                self.list.insertItem(offset, item)
            else:
                self.list.addItem(item)
        self._apply_filter(self.filter.text())
        return self

    def _pick(self, item):
        cls = item.data(_CLASS_ROLE)
        if cls and self._onPick is not None:
            self._onPick(cls)

    def _filter_changed(self, text):
        self._apply_filter(text)

    def _apply_filter(self, text):
        needle = str(text or "").strip().lower()
        header, shown_in_group = None, 0
        for i in range(self.list.count()):
            item = self.list.item(i)
            if item.data(_CLASS_ROLE) is None:
                if header is not None:
                    header.setHidden(shown_in_group == 0)
                header, shown_in_group = item, 0
                continue
            shown = needle in item.text().lower()
            item.setHidden(not shown)
            shown_in_group += int(shown)
        if header is not None:
            header.setHidden(shown_in_group == 0)

    @method({"handler": "fun(class: string)"}, returns="self",
            doc="Called with the class name, e.g. 'ui.Button', when an item "
                "is double-clicked.")
    def setOnPick(self, handler):
        self._onPick = guard(handler, widget="WidgetPalette", event="onPick")
        return self

    @method({"icons": "table<string, string>"}, returns="self",
            doc="Icons for the items, as {['ui.Button'] = 'path/to/icon.png'}. "
                "A class without one keeps a blank space, so names line up.")
    def setIcons(self, icons):
        icons = as_mapping(icons)
        blank = QIcon()
        for i in range(self.list.count()):
            item = self.list.item(i)
            cls = item.data(_CLASS_ROLE)
            if cls:
                path = icons.get(cls)
                item.setIcon(QIcon(str(path)) if path else blank)
        return self

    @method(returns="string", doc="The class of the selected item, or nil.")
    def getSelectedClass(self):
        item = self.list.currentItem()
        return item.data(_CLASS_ROLE) if item is not None else None

    @method({"text": "string"}, returns="self",
            doc="Hides items whose name does not contain the text. A group "
                "header hides when its whole group does.")
    def setFilter(self, text):
        text = str(text or "")
        if self.filter.text() != text:
            self.filter.setText(text)      # textChanged applies it
        else:
            self._apply_filter(text)
        return self

    @method(returns="string[]", doc="Every class the palette offers.")
    def getClasses(self):
        classes = palette_classes()
        try:
            return to_lua(classes)
        except BridgeError:
            return classes
