from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Qt
from limekit.framework.core.engine.parts import EnginePart


class Slider(QSlider, EnginePart):
    onValueChangeFunc = None

    def __init__(self, orientation="horizontal"):
        qt_orie = Qt.Orientation.Horizontal

        if orientation == "horizontal":
            qt_orie = Qt.Orientation.Horizontal

        elif orientation == "vertical":
            qt_orie = Qt.Orientation.Vertical

        super().__init__(qt_orie)

        self.valueChanged.connect(self.__handleValueChanged)

    def setOnValueChange(self, onValueChangeFunc):
        self.onValueChangeFunc = onValueChangeFunc

    def __handleValueChanged(self):
        if self.onValueChangeFunc:
            self.onValueChangeFunc(self, self.value())

    def setValue(self, value):
        super().setValue(value)

    def getValue(self):
        return self.value()
