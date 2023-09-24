from PySide6.QtWidgets import QListWidget
from limekit.framework.core.engine.parts import EnginePart


class ListBox(EnginePart, QListWidget):
    def __init__(self):
        super().__init__()

    def onItemSelect(self, func):
        self.currentItemChanged.connect(lambda: func(self, self.currentItem().text()))

    def getSelectedItem(self):
        return self.currentText()

    def setItem(self, *items):
        for item in items:
            self.addItem(str(item))
