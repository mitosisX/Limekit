from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QListWidget, QListWidgetItem

from limekit.kernel.bridge.convert import as_sequence
from limekit.kernel.coerce import LuaIndex
from limekit.kernel.spec import Event
from limekit.widgets.base import LimeWidget


class ListBox(LimeWidget, QListWidget):
    __lime__ = "ui.ListBox"

    onItemSelect = Event("currentItemChanged", passes_self=True)
    onItemDoubleClick = Event("itemDoubleClicked", passes_self=True)

    def __init__(self, items=None):
        super().__init__()
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
            self.addItem(QListWidgetItem(str(item)))
        return self

    def addImageItem(self, label, image):
        item = QListWidgetItem(str(label))
        item.setIcon(QIcon(image))
        self.addItem(item)
        return self

    def getItemsCount(self):
        return self.count()

    def getItemAt(self, index):
        """1-indexed, like every other Limekit collection accessor."""
        item = self.item(LuaIndex(index))
        return item.text() if item else None
