from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from limekit.engine.parts import EnginePart
from limekit.components.base.widget_base import BaseWidget


class Container(BaseWidget, QWidget, EnginePart):
    onKeyPressFunc = None

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    # Allows adding child without setting a layout
    def createContainer(self, child):
        return self.createWindowContainer(child)

    def setOnKeyPress(self, onKeyPressFunc):
        self.onKeyPressFunc = onKeyPressFunc

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

    def keyPressEvent(self, event):
        if self.onKeyPressFunc:
            return self.onKeyPressFunc(self, event)
