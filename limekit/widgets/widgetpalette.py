"""A list of every widget the designer can build, that can be dragged from.

Only classes `Introspect.buildableClasses()` reports are offered, and only
the ones that are widgets, so nothing in the list fails the moment it is
dropped. Grouping is a static table; a class added to Limekit without being
added here still appears, under "Other", rather than silently vanishing
from the palette.
"""

from PySide6.QtCore import QMimeData, Qt
from PySide6.QtWidgets import (QLineEdit, QListWidget, QListWidgetItem,
                               QVBoxLayout, QWidget)

from limekit.kernel.bridge.convert import to_lua
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
    "Window", "Modal", "Dock", "Dockable", "Menu", "DropMenu", "Toolbar",
    "TabItem", "SlidingStackedWidget", "DesignSurface", "WidgetPalette",
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


class WidgetPalette(LimeWidget, QWidget):
    __lime__ = "ui.WidgetPalette"

    def __init__(self):
        super().__init__()
        self._onPick = None

        self.filter = QLineEdit()
        self.filter.setPlaceholderText("Search widgets")
        self.filter.setClearButtonEnabled(True)

        self.list = _PaletteList()
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

    def _fill(self):
        for title, classes in grouped():
            header = QListWidgetItem(title)
            header.setFlags(Qt.ItemFlag.NoItemFlags)
            font = header.font()
            font.setBold(True)
            header.setFont(font)
            self.list.addItem(header)
            for cls in classes:
                item = QListWidgetItem(cls[3:])
                item.setData(_CLASS_ROLE, cls)
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
                              | Qt.ItemFlag.ItemIsDragEnabled)
                self.list.addItem(item)

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
