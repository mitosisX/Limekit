from limekit.engine.parts import EnginePart
from limekit.components.widgets.items.tableitem import TableItem

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView
from PySide6.QtCore import Qt, QItemSelection
from PySide6.QtGui import QPixmap, QIcon
from limekit.utils.converters import Converter

"""
To set the number of columns of available
    table.setColumnCount(num)

For rows
    table.setRowCount(num)

Additonally, each column can be provided a width, using the table.setColumnWidth(column, width).
Each column starts at index 0

The constructor can be explicity passes number of rows and column and its parent too
"""


class Table(QTableWidget, EnginePart):
    cellEditFinishedFunc = None
    cellClickedFunc = None
    cellDoubleClickedFunc = None
    cellSelctionDoneFunc = None

    def __init__(self, rows=None, columns=None, parent=None):
        super().__init__(rows, columns, parent)
        self.cellChanged.connect(self.__onCellEditFinished)
        self.cellClicked.connect(self.__onCellClicked)
        self.cellDoubleClicked.connect(self.__onCellDoubleClicked)
        self.selectionModel().selectionChanged.connect(self.__handleCellSelectionDone)

    # Events ----------------

    def setOnCellEditFinished(self, cellEditFinishedFunc):
        self.cellEditFinishedFunc = cellEditFinishedFunc

    def __onCellEditFinished(self, row, column):
        if self.cellEditFinishedFunc:
            self.cellEditFinishedFunc(self, row, column)

    def setOnCellClicked(self, cellClickedFunc):
        self.cellClickedFunc = cellClickedFunc

    def __onCellClicked(self, row, column):
        if self.cellClickedFunc:
            self.cellClickedFunc(self, row, column)

    def setOnCellDoubleClicked(self, cellDoubleClickedFunc):
        self.cellDoubleClickedFunc = cellDoubleClickedFunc

    def __onCellDoubleClicked(self, row, column):
        if self.cellDoubleClickedFunc:
            self.cellDoubleClickedFunc(self, row, column)

    def setOnCellSelection(self, cellSelctionDoneFunc):
        self.cellSelctionDoneFunc = cellSelctionDoneFunc

    def __handleCellSelectionDone(self, selected, deselected):
        if self.cellSelctionDoneFunc:
            self.cellSelctionDoneFunc(self, self.currentRow(), self.currentColumn())

    # def onCellEditFinish(self, func):
    #     self.cellChanged.connect(
    #         lambda row, column: self.__handleCellEdit(row, column, func)
    #     )

    # def __handleCellEdit(self, row, column, func):
    #     func(self, row, column)

    # ---------------- Events

    def addData(self, row, column, data):
        self.setItem(row, column, QTableWidgetItem(str(data)))

    def setTableData(self, data):
        dict_ = data
        self.setItem(dict_.row, dict_.column, QTableWidgetItem(dict_.text))

    def setImageData(self, image, text, row, column):
        item = QTableWidgetItem()

        # Set text for the item
        item.setText(text)

        # Load an image using QPixmap
        pixmap = QPixmap(image)

        # Set the image for the item
        # item.setData(1, pixmap)
        item.setIcon(QIcon(pixmap))

        # Add the item to the table
        self.setItem(row, column, item)

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

    def getCurrentColumn(self):
        return self.currentColumn()

    def getCurrentRow(self):
        return self.currentRow()

    # Get all column available
    def getColumnsCount(self):
        self.columnCount()

    # Get all rows available
    def getRowsCount(self):
        self.rowCount()

    def setGridVisible(self, visibility):
        self.setShowGrid(visibility)

    # Hides the 1,2,3,4,5 in rows: top - bottom
    def setRowLabelsVisible(self, visibility):
        self.verticalHeader().setVisible(visibility)

    # Allows adding widgets to cells
    def setCellChild(self, row, column, child):
        self.setCellWidget(row, column, child)

    # Automatically resize all columns to fit content length
    def setAutoColumnResize(self):
        self.resizeColumnsToContents()

    def setAutoRowResize(self):
        self.resizeRowsToContents()

    # Set a specified row to resize to content length
    def setRowFitsContent(self, row):
        self.resizeRowToContents(row)

    def setColumnFitsContent(self, column):
        self.resizeColumnToContents(column)

    def deleteRow(self, row):
        self.removeRow(row)

    def setCellsEditable(self, editable):
        self.setEditTriggers(
            QAbstractItemView.EditTrigger.AllEditTriggers
            if editable
            else QAbstractItemView.EditTrigger.NoEditTriggers
        )

    def setAltRowColors(self, setAlt):
        self.setAlternatingRowColors(setAlt)

    # Whether to allow column headers to be sorted
    def setColumnSorting(self, sorting):
        self.setSortingEnabled(sorting)

    # Clearing --------------
    def clear(self):
        # Resets the whole table
        super().clear()

    def clearContent(self):
        # Only removes data inside the table cells and rows
        self.clearContents()

    # -------------- Clearing

    def findDataItem(self, item):
        lis = self.findItems(item, Qt.MatchFlag.MatchContains)
        return lis

    def insertColumnAt(self, position):
        self.insertColumn(position)

    def insertRowAt(self, position):
        self.insertRow(position)

    def removeColumnAt(self, position):
        self.removeColumn(position)

    def removeRowAt(self, position):
        self.removeRow(position)

    def getItemAt(self, row, column):
        item = self.item(row, column)
        return TableItem(item) or None

    def getSelectedCells(self):
        cells = []
        aa = self.selectedIndexes()
        selected_items = set((idx.row(), idx.column()) for idx in aa)

        # Print the text in the selected cells
        for item in selected_items:
            row, column = item

            return Converter.table_from([row, column])
            # print(TableItem(self.getItemAt(row, column)))  # .setBackgroundHex("#fff"))
            # cells.append(TableItem(item))

        return Converter.table_from(cells)

    def getSelectedCell(self):
        item = self.currentItem()
        return TableItem(item) or None

    # research what it does
    def setSpan(self, row, column, rowSpan, columnSpan):
        super().setSpan(row, column, rowSpan, columnSpan)
