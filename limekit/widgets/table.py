"""Table.

Every row/column-taking Qt method needs a `LuaIndex` translation, and a
`Prop` has no way to transform an index argument -- so almost nothing here
is a plain Prop. Two collisions the collision guard would (correctly) catch
if this were written more naively:

- A `rowCount` Prop generates `getRowCount`/`setRowCount`. Those happen to
  be the exact real Qt method names, which the guard allows as an
  intentional shadow -- but this class also wants a hand-written
  `setRowCount` that coerces its argument through `_to_int` with a
  Limekit-flavoured error message, and *that* collides with the
  Prop-generated one. Both `rowCount` and `columnCount` are hand-written
  methods instead, not Props.
- A Prop meant to expose "the current item" and naively named `item` would
  generate `setItem` -- shadowing `QTableWidget.setItem(row, column, item)`,
  a real, differently-shaped method, not the one the Prop meant to wrap.
  Every cell accessor here is hand-written and named around what it does
  (`getCellItem`, `getCurrentItem`) rather than colliding on `item`.
"""

from PySide6.QtGui import QBrush
from PySide6.QtWidgets import QAbstractItemView, QTableWidget, QTableWidgetItem

from limekit.kernel.bridge.convert import as_sequence
from limekit.kernel.coerce import Colour, Enum, LuaIndex
from limekit.kernel.declarative import LimeObject
from limekit.kernel.spec import Event, Prop
from limekit.widgets.base import LimeWidget, _to_int

_SELECTION_BEHAVIORS = {
    "items": QAbstractItemView.SelectionBehavior.SelectItems,
    "rows": QAbstractItemView.SelectionBehavior.SelectRows,
    "columns": QAbstractItemView.SelectionBehavior.SelectColumns,
}
_selection_behavior = Enum(_SELECTION_BEHAVIORS, "selection behavior")


class TableItem(LimeObject, QTableWidgetItem):
    __lime__ = "ui.TableItem"

    text = Prop(str, qt=("text", "setText"), coerce=str)

    def __init__(self, text=""):
        super().__init__(str(text))

    def setBackgroundColour(self, colour):
        self.setBackground(QBrush(Colour(colour)))
        return self

    def setTextColour(self, colour):
        self.setForeground(QBrush(Colour(colour)))
        return self


class Table(LimeWidget, QTableWidget):
    __lime__ = "ui.Table"

    showGrid = Prop(bool, qt=("showGrid", "setShowGrid"))
    sortingEnabled = Prop(bool, qt=("isSortingEnabled", "setSortingEnabled"))
    alternatingRowColors = Prop(bool, qt=("alternatingRowColors", "setAlternatingRowColors"))

    onCellClick = Event("cellClicked", passes_self=True,
                        params=(("row", "integer"), ("column", "integer")),
                        indices=("row", "column"),
                        doc="Fired when a cell is clicked. row and column are 1-based.")
    onCellDoubleClick = Event("cellDoubleClicked", passes_self=True,
                              params=(("row", "integer"), ("column", "integer")),
                              indices=("row", "column"),
                              doc="Fired when a cell is double-clicked. row and column are 1-based.")
    onCellChange = Event("cellChanged", passes_self=True,
                         params=(("row", "integer"), ("column", "integer")),
                         indices=("row", "column"),
                         doc="Fired when a cell's contents change. row and column are 1-based.")

    def __init__(self, rows=0, columns=0):
        super().__init__(_to_int(rows, "rows"), _to_int(columns, "columns"))
        self.setAlternatingRowColors(True)

    # -- structure -----------------------------------------------------

    def setRowCount(self, rows):
        super().setRowCount(_to_int(rows, "rows"))
        return self

    def getRowCount(self):
        return self.rowCount()

    def setColumnCount(self, columns):
        super().setColumnCount(_to_int(columns, "columns"))
        return self

    def getColumnCount(self):
        return self.columnCount()

    def setColumnHeaders(self, headers):
        header_list = [str(h) for h in as_sequence(headers)]
        self.setColumnCount(len(header_list))
        super().setHorizontalHeaderLabels(header_list)
        return self

    def setRowHeaders(self, headers):
        header_list = [str(h) for h in as_sequence(headers)]
        super().setVerticalHeaderLabels(header_list)
        return self

    def getColumnHeaderText(self, column):
        item = self.horizontalHeaderItem(LuaIndex(column))
        return item.text() if item else None

    def setColumnWidth(self, column, width):
        super().setColumnWidth(LuaIndex(column), _to_int(width, "width"))
        return self

    def insertRowAt(self, row):
        self.insertRow(LuaIndex(row))
        return self

    def insertColumnAt(self, column):
        self.insertColumn(LuaIndex(column))
        return self

    def removeRowAt(self, row):
        self.removeRow(LuaIndex(row))
        return self

    def removeColumnAt(self, column):
        self.removeColumn(LuaIndex(column))
        return self

    def addRow(self):
        """Append a row at the end; returns its 1-indexed position."""
        position = self.rowCount()
        self.insertRow(position)
        return position + 1

    # -- cells -----------------------------------------------------------

    def setCellText(self, row, column, text):
        super().setItem(LuaIndex(row), LuaIndex(column), TableItem(text))
        return self

    def getCellItem(self, row, column):
        return self.item(LuaIndex(row), LuaIndex(column))

    def setCellChild(self, row, column, child):
        self.setCellWidget(LuaIndex(row), LuaIndex(column), child)
        return self

    def getCellChild(self, row, column):
        return self.cellWidget(LuaIndex(row), LuaIndex(column))

    def getCurrentItem(self):
        return self.currentItem()

    def getCurrentRow(self):
        return self.currentRow() + 1

    def getCurrentColumn(self):
        return self.currentColumn() + 1

    def setCurrentCell(self, row, column):
        super().setCurrentCell(LuaIndex(row), LuaIndex(column))
        return self

    # -- behaviour ---------------------------------------------------------

    def setSelectionBehavior(self, behavior):
        super().setSelectionBehavior(_selection_behavior(behavior))
        return self

    def setCellsEditable(self, editable):
        self.setEditTriggers(
            QAbstractItemView.EditTrigger.AllEditTriggers if editable
            else QAbstractItemView.EditTrigger.NoEditTriggers
        )
        return self

    def clear(self):
        super().clear()
        return self

    def clearContent(self):
        super().clearContents()
        return self
