from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from limekit.engine.parts import EnginePart
from limekit.components.base.widget_base import BaseWidget


class Container(BaseWidget, QWidget, EnginePart):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def setLayout(self, layout):
        super().setLayout(layout)

    def setSize(self, width, height):
        super().resize(width, height)

    def getChild(self):
        return self.widget()

    def getLayout(self):
        return self.layout()

    def setStyle(self, style):
        self.setStyleSheet(style)
