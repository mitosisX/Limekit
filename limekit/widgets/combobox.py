from PySide6.QtWidgets import QComboBox

from limekit.kernel.bridge.convert import as_sequence
from limekit.kernel.coerce import LuaIndex
from limekit.kernel.spec import Event, Prop, method
from limekit.widgets.base import LimeWidget


class ComboBox(LimeWidget, QComboBox):
    __lime__ = "ui.ComboBox"

    editable = Prop(bool, qt=("isEditable", "setEditable"))

    onItemSelect = Event("currentIndexChanged", passes_self=True,
                          params=(("index", "integer"),),
                          indices=("index",),
                          doc="Fired when the selection changes. index is 1-based; "
                              "0 means nothing is selected.")

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

    def clear(self):
        """Qt native re-exposed so Lua's `box:clear()` colon syntax works."""
        super().clear()
        return self

    @method({"text": "string"}, returns="self",
            doc="Appends one item to the end of the list.")
    def addItem(self, text):
        QComboBox.addItem(self, str(text))
        return self

    @method({"items": "string[]"}, returns="self",
            doc="Appends several items, from a table of strings.")
    def addItems(self, items):
        for item in as_sequence(items):
            self.addItem(item)
        return self
