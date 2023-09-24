from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Qt
from limekit.framework.core.engine.parts import EnginePart


class Slider(EnginePart, QSlider):
    def __init__(self):
        super().__init__(Qt.Horizontal)

    def onValueChange(self, func):
        self.valueChanged[int].connect(lambda: func(self, self.value()))
