from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtGui import QColor, QBrush


class TableItem(EnginePart):
    def __init__(self, item: QTableWidgetItem):
        self.item = item

    def getText(self):
        return self.item.text()

    def setText(self, text):
        if self.item:
            self.item.setText(text)

    def setBackgroundRGB(self, r, g, b):
        self.item.setBackground(QBrush(QColor(r, g, b)))

    def setBackgroundHex(self, hex):
        self.item.setBackground(QBrush(QColor(hex)))

    def setTextColorHex(self, hex):
        self.item.setForeground(QBrush(QColor(hex)))

    def setTextColorRGB(self, r, g, b):
        self.item.setForeground(QBrush(QColor(r, g, b)))
