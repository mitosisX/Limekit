from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.components.base.base_widget import BaseWidget


class Container(QWidget, BaseWidget, EnginePart):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        BaseWidget.__init__(self, widget=self)

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
