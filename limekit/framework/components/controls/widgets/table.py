from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtWidgets import QAbstractItemView

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

    def onCellEditFinish(self, func):
        self.cellChanged.connect(
            lambda row, column: self.__handleCellEdit(row, column, func)
        )

    def __handleCellEdit(self, row, column, func):
        func(self, row, column)

    def setData(self, row, column, data):
        self.setItem(row, column, QTableWidgetItem(data))

    def setColumnHeaders(self, headers):
        self.setHorizontalHeaderLabels(headers.values())

    def setRowHeaders(self, headers):
        self.setVerticalHeaderLabels(headers.values())

    def setMaxColumns(self, columns):
        self.setColumnCount(columns)

    def setMaxRows(self, rows):
        self.setRowCount(rows)

    # Can only be set after headers have been applied
    def setColumnHeaderToolTip(self, header, tooltip):
        self.horizontalHeaderItem(header).setToolTip(tooltip)

    # The header number you want to get the text of
    def getColumnHeaderText(self, num):
        return self.horizontalHeaderItem(num).text()

    def setGridVisible(self, visibility):
        self.setShowGrid(visibility)

    # Hides the 1,2,3,4,5 in rows: top - bottom
    def setRowLabelsVisible(self, visibility):
        self.verticalHeader().setVisible(visibility)

    # Allows adding widgets to cells
    def setCellChild(self, row, column, child):
        self.setCellWidget(row, column, child)

    def getRowsCount(self):
        return self.rowCount()

    def deleteRows(self, rows):
        self.removeRow(rows)

    def setCellsEditable(self, editable=True):
        self.setEditTriggers(
            QAbstractItemView.AllEditTriggers
            if editable
            else QAbstractItemView.NoEditTriggers
        )

    def setAltRowColors(self, setAlt):
        self.setAlternatingRowColors(setAlt)

    # Whether to allow column headers to be sorted
    def setColumnSorting(self, sorting):
        self.setSortingEnabled(sorting)
