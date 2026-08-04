from PySide6.QtWidgets import QFormLayout

from limekit.kernel.coerce import LuaIndex
from limekit.layouts.base import LimeLayout


class FormLayout(LimeLayout, QFormLayout):
    """Label/field pairs, one per row."""

    __lime__ = "ui.FormLayout"

    def __init__(self, parent=None):
        super().__init__(parent)

    def addChild(self, title, child=None):
        """`addChild("Name", field)` for a labelled row, or `addChild(widget)`
        (title is actually the widget) for a full-width unlabelled one -
        mirrors QFormLayout.addRow's own two call shapes."""
        if isinstance(title, str):
            self.addRow(title, child)
        else:
            self.addRow(title)
        return self

    def addLayout(self, title, layout):
        self.addRow(str(title), layout)
        return self

    def getRowAt(self, index):
        """1-indexed, like every other Limekit collection accessor."""
        item = self.itemAt(LuaIndex(index), QFormLayout.ItemRole.FieldRole)
        return item.widget() if item else None
