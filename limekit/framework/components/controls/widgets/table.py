from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from limekit.framework.core.engine.parts import EnginePart

"""
To set the number of columns of available
    table.setColumnCount(num)

For rows
    table.setRowCount(num)

Additonally, each column can be provided a width, using the table.setColumnWidth(column, width).
Each column starts at index 0

The constructor can be explicity passes number of rows and column and its parent too
"""


class TableGrid(EnginePart, QTableWidget):
    def __init__(self, rows=None, columns=None, parent=None):
        super().__init__(rows, columns, parent)

        # super().__init__(rows, columns, parent)

    def onCellEditFinish(self, func):
        self.cellChanged.connect(
            lambda row, column: self.__handleCellEdit(row, column, func)
        )

    def __handleCellEdit(self, row, column, func):
        func(self, row, column)

    def setData(self, row, column, data):
        self.setItem(row, column, QTableWidgetItem(data))
