from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from limekit.framework.core.engine.parts import EnginePart


# Might be needed somewhere
class Container(QWidget, EnginePart):
    # name = "Container"

    def __init__(self):
        super().__init__()

    def __init__(self, parent=None):
        super().__init__(parent)

    def setLayout(self, layout):
        super().setLayout(layout)

    def setSize(self, width, height):
        super().resize(width, height)
