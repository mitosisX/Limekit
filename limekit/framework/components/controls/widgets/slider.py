from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Qt
from limekit.framework.core.engine.parts import EnginePart


class Slider(QSlider, EnginePart):
    onValueChangeFunc = None

    def __init__(self):
        super().__init__(Qt.Horizontal)

    def setOnValueChange(self, func):
        self.valueChanged.connect(lambda: func(self, self.value()))
