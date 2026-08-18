from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QListWidget, QListWidgetItem

from limekit.kernel.bridge.convert import as_mapping, as_sequence
from limekit.kernel.coerce import LuaIndex
from limekit.kernel.errors import BridgeError
from limekit.kernel.bridge.guard import guard
from limekit.kernel.spec import method
from limekit.widgets.base import LimeWidget


class ListBox(LimeWidget, QListWidget):
    __lime__ = "ui.ListBox"

    # Hand-written rather than declarative: the Qt signals carry
    # QListWidgetItem objects, which are useless to a Lua caller -- there is
    # nothing it can do with one. 1.x passed (widget, text, row) and that is
    # what these pass, the same reasoning that makes Tab's attachers
    # hand-written. Rows are 1-based, like every other index.

    def __init__(self, items=None):
        super().__init__()
        self._onItemSelect = None
        self._onItemDoubleClick = None
        self.currentItemChanged.connect(self._handleItemSelect)
        self.itemDoubleClicked.connect(self._handleItemDoubleClick)
        self.setAlternatingRowColors(True)
        if items is not None:
            self.setItems(items)

    def setItems(self, items):
        """Accepts a Lua table OR a Python sequence.

        The old implementation called .values() unconditionally and crashed
        on a Python list, unlike ComboBox.
        """
        self.clear()
        for item in as_sequence(items):
            QListWidget.addItem(self, QListWidgetItem(str(item)))
        return self

    def addImageItem(self, label, image):
        item = QListWidgetItem(str(label))
        item.setIcon(QIcon(image))
        # QListWidget.addItem, not self.addItem: the Lua-facing addItem takes
        # a string and str()s whatever it is given, which turned an item
        # object into its repr and printed
        # "<PySide6.QtWidgets.QListWidgetItem object at 0x...>" in the list.
        QListWidget.addItem(self, item)
        return self

    def getItemsCount(self):
        return self.count()

    def getCurrentRow(self):
        """1-indexed. Returns 0 when nothing is selected.

        Qt's currentRow() is 0-based and returns -1 for "no selection";
        exposing that directly would break the 1-indexed contract every
        other Limekit collection accessor keeps.
        """
        return self.currentRow() + 1

    def setCurrentRow(self, row):
        super().setCurrentRow(LuaIndex(row))
        return self

    def insertItemAt(self, row, item):
        self.insertItem(LuaIndex(row), QListWidgetItem(str(item)))
        return self

    def removeItemAt(self, row):
        item = self.takeItem(LuaIndex(row))
        if item is None:
            raise BridgeError(f"no item at row {row}")
        del item
        return self

    def getItemAt(self, index):
        """1-indexed, like every other Limekit collection accessor."""
        item = self.item(LuaIndex(index))
        return item.text() if item else None

    def clear(self):
        """Qt native re-exposed so Lua's `box:clear()` colon syntax works."""
        super().clear()
        return self

    @method({"items": "table<string, string>"}, returns="self",
            doc="Adds several icon+label entries at once, from a table of "
                "label -> image path.")
    def addImageItems(self, items):
        for label, image in as_mapping(items).items():
            self.addImageItem(label, image)
        return self

    @method({"text": "string"}, returns="self",
            doc="Appends one item to the end of the list.")
    def addItem(self, text):
        """setItems replaces everything; there was no way to append a single
        item, which is what a list being filled incrementally actually needs.

        Takes a string. Code inside this class that already holds a
        QListWidgetItem calls QListWidget.addItem directly.
        """
        QListWidget.addItem(self, str(text))
        return self

    @method({"items": "string[]"}, returns="self",
            doc="Appends several items, from a table of strings.")
    def addItems(self, items):
        for item in as_sequence(items):
            self.addItem(item)
        return self

    # -- events ------------------------------------------------------------

    @method({"handler": "fun(widget: ListBox, text: string, row: integer)"},
            returns="self",
            doc="Runs when the selected item changes. The handler receives the "
                "list, the selected text, and its 1-based row.")
    def setOnItemSelect(self, handler):
        self._onItemSelect = guard(handler, widget="ListBox", event="onItemSelect")
        return self

    @method({"handler": "fun(widget: ListBox, text: string, row: integer)"},
            returns="self",
            doc="Runs when an item is double-clicked. The handler receives the "
                "list, the item's text, and its 1-based row.")
    def setOnItemDoubleClick(self, handler):
        self._onItemDoubleClick = guard(
            handler, widget="ListBox", event="onItemDoubleClick"
        )
        return self

    def _handleItemSelect(self, current, previous):
        if self._onItemSelect and current is not None:
            self._onItemSelect(self, current.text(), self.getCurrentRow())

    def _handleItemDoubleClick(self, item):
        if self._onItemDoubleClick:
            self._onItemDoubleClick(self, item.text(), self.getCurrentRow())
