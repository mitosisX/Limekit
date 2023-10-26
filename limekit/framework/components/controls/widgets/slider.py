from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Qt
from limekit.framework.core.engine.parts import EnginePart


class Slider(QSlider, EnginePart):
    onValueChangeFunc = None

    def __init__(self, orientation="horizontal"):
        qt_orie = Qt.Horizontal

        match (orientation):
            case ("horizontal"):
                qt_orie = Qt.Horizontal
            case ("vertical"):
                qt_orie = Qt.Vertical

        super().__init__(qt_orie)

    def setOnValueChange(self, func):
        self.valueChanged.connect(lambda: func(self, self.value()))
