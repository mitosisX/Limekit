from PySide6.QtWidgets import QGridLayout

from limekit.kernel.coerce import LuaIndex
from limekit.layouts.base import LimeLayout, _to_int


class GridLayout(LimeLayout, QGridLayout):
    """Positions children by row and column.

    Rows and columns are **1-indexed**, like every other Limekit collection
    coordinate. The 1.x GridLayout took raw 0-based Qt indices while its
    sibling layouts subtracted 1 -- that inconsistency is gone.
    """

    __lime__ = "ui.GridLayout"

    def __init__(self, parent=None):
        super().__init__(parent)

    def addChild(self, child, row, column, rowSpan=1, columnSpan=1):
        self.addWidget(
            child, LuaIndex(row), LuaIndex(column),
            _to_int(rowSpan, "rowSpan"), _to_int(columnSpan, "columnSpan"),
        )
        return self

    def addLayout(self, layout, row, column, rowSpan=1, columnSpan=1):
        super().addLayout(
            layout, LuaIndex(row), LuaIndex(column),
            _to_int(rowSpan, "rowSpan"), _to_int(columnSpan, "columnSpan"),
        )
        return self

    def getChildAt(self, row, column):
        item = self.itemAtPosition(LuaIndex(row), LuaIndex(column))
        return item.widget() if item else None

    def setColumnStretch(self, column, stretch):
        super().setColumnStretch(LuaIndex(column), _to_int(stretch, "stretch"))
        return self

    def setRowStretch(self, row, stretch):
        super().setRowStretch(LuaIndex(row), _to_int(stretch, "stretch"))
        return self
