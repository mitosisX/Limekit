from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.handle.scripts.swissknife.converters import Converter


class ListBox(QListWidget, EnginePart):
    onCurrentItemChangeFunc = None

    def __init__(self, items=None):
        # By defaulf, the ViewMode is on ListMode
        super().__init__()
        if items:
            self.setItems(items)

        self.setAlternatingRowColors(True)
        self.currentItemChanged.connect(self.__handleItemSelect)

    def setOnItemSelect(self, onCurrentItemChangeFunc):
        self.onCurrentItemChangeFunc = onCurrentItemChangeFunc

    def __handleItemSelect(self):
        if self.onCurrentItemChangeFunc:
            self.onCurrentItemChangeFunc(self, self.currentItem().text())

    def setItemViewMode(self, view_type):
        match (view_type):
            case ("icons"):
                self.setViewMode(QListWidget.ViewMode.IconMode)
            case ("list"):
                self.setViewMode(QListWidget.ViewMode.ListMode)

    def getSelectedItem(self):
        return self.currentText()

    def addItem(self, item):
        super().addItem(QListWidgetItem(item))

    def setItems(self, items):
        for item in items.values():
            self.addItem(item)

    def addImageItem(self, label, image):
        item = QListWidgetItem(label)
        item.setIcon(QIcon(image))
        self.addItem(item)

    def addImageItems(self, items):
        for item, image in items.items():
            self.addImageItem(item, image)

    def addItems(self, items):
        for item in items.values():
            super().addItem(QListWidgetItem(item))

    def removeItem(self, row):
        item = self.takeItem(row)
        del item

    def getCurrentRow(self):
        return self.currentRow()

    def insertItemAt(self, row, item):
        self.insertItem(row, QListWidgetItem(item))

    # This gives the widget the grey and white separation colors
    def setAltRowColors(self, bool_):
        self.setAlternatingRowColors(bool_)

    def setIconSizes(self, width, height):
        self.setIconSize(QSize(width, height))

    def getItemAt(self, at):
        item = self.item(at)
        return item.text() if item else None

    def clearItems(self):
        self.clear()

    # Whether dragging items onto this is allowed
    def setAllowDragDrop(self, enable: bool):
        self.setAcceptDrops(enable)

    def setEnableDrag(self, enable: bool):
        self.setDragEnabled(enable)
