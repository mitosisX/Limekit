from PySide6.QtWidgets import QComboBox

from limekit.kernel.bridge.convert import as_sequence
from limekit.kernel.coerce import LuaIndex
from limekit.kernel.spec import Event, Prop
from limekit.widgets.base import LimeWidget


class ComboBox(LimeWidget, QComboBox):
    __lime__ = "ui.ComboBox"

    editable = Prop(bool, qt=("isEditable", "setEditable"))

    onItemSelect = Event("currentIndexChanged", passes_self=True)

    def __init__(self, items=None):
        super().__init__()
        if items is not None:
            self.setItems(items)

    def setItems(self, items):
        self.clear()
        for item in as_sequence(items):
            self.addItem(str(item))
        return self

    def getText(self):
        return self.currentText()

    def getItemAt(self, index):
        return self.itemText(LuaIndex(index))
