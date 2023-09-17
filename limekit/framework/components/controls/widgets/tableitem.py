from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtWidgets import QTableWidgetItem


class TableItem(EnginePart):
    def __init__(self, item: QTableWidgetItem):
        self.item = item

    def getText(self):
        return self.item.text()

    def setText(self, text):
        self.item.setText(text)
