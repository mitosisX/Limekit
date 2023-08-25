from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from limekit.framework.core.engine.parts import EnginePart


# Might be needed somewhere
class Widget(EnginePart, QWidget):
    def __init__(self):
        super().__init__()
