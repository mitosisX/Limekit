from PySide6.QtWidgets import QComboBox

from limekit.kernel.bridge.convert import as_sequence
from limekit.kernel.coerce import LuaIndex
from limekit.kernel.spec import Event, Prop
from limekit.widgets.base import LimeWidget


class ComboBox(LimeWidget, QComboBox):
    __lime__ = "ui.ComboBox"

    editable = Prop(bool, qt=("isEditable", "setEditable"))

    onItemSelect = Event("currentIndexChanged", passes_self=True,
                          params=(("index", "integer"),),
                          doc="Fired when the selection changes. NOTE: index is the raw Qt "
                              "0-based position, not 1-based like the rest of the API.")

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
