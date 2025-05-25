from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from limekit.engine.parts import EnginePart
from limekit.components.base.widget_base import BaseWidget
from limekit.utils.converters import Converter


class ListBox(BaseWidget, QListWidget, EnginePart):
    onCurrentItemChangeFunc = None
    onDoubleClickCurrentItemChangeFunc = None

    def __init__(self, items=None):
        # By defaulf, the ViewMode is on ListMode
        super().__init__(parent=None)

        if items:
            self.setItems(items)

        self.setAltRowColors(True)
        self.currentItemChanged.connect(self.__handleItemSelect)
        self.itemDoubleClicked.connect(self.__handleItemDoubleClick)

    def setOnItemSelect(self, onCurrentItemChangeFunc):
        self.onCurrentItemChangeFunc = onCurrentItemChangeFunc

    def __handleItemSelect(self):
        if self.onCurrentItemChangeFunc:
            self.onCurrentItemChangeFunc(
                self, self.currentItem().text(), self.getCurrentRow()
            )

    def setOnItemDoubleClick(self, onDoubleClickCurrentItemChangeFunc):
        self.onDoubleClickCurrentItemChangeFunc = onDoubleClickCurrentItemChangeFunc

    def __handleItemDoubleClick(self, item):
        if self.onDoubleClickCurrentItemChangeFunc:
            self.onDoubleClickCurrentItemChangeFunc(
                self, item.text(), self.getCurrentRow()
            )

    def setItemViewMode(self, view_type):
        if view_type == "icons":
            self.setViewMode(QListWidget.ViewMode.IconMode)
        elif view_type == "list":
            self.setViewMode(QListWidget.ViewMode.ListMode)

    def setItems(self, items):
        for item in items.values():
            self.addItem(str(item))

    def getText(self):
        return self.currentText()

    def addItem(self, item):
        super().addItem(QListWidgetItem(item))

    def addItems(self, items):
        for item in items.values():
            super().addItem(QListWidgetItem(item))

    def addImageItem(self, label, image):
        item = QListWidgetItem(label)
        item.setIcon(QIcon(image))
        self.addItem(item)

    def addImageItems(self, items):
        for item, image in items.items():
            self.addImageItem(item, image)

    def removeItem(self, row):
        item = self.takeItem(row)
        del item

    def getCurrentRow(self):
        return self.currentRow()

    def getItemsCount(self):
        return self.count()

    def insertItemAt(self, row, item):
        self.insertItem(row, QListWidgetItem(item))

    # This gives the widget the grey and white separation colors
    def setAltRowColors(self, bool_):
        self.setAlternatingRowColors(bool_)

    def setIconSizes(self, width, height):
        self.setIconSize(QSize(width, height))

    def getTextAt(self, at):
        item = self.item(at)
        return item.text() if item else None

    def getItemAt(self, at):
        item = self.item(at)
        return item.text() if item else None

    def clear(self):
        super().clear()

    # Whether dragging items onto this is allowed
    def setAllowDragDrop(self, enable: bool):
        self.setAcceptDrops(enable)

    def setDragEnabled(self, enable: bool):
        super().setDragEnabled(enable)
