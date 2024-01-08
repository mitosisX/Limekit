from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Qt
from limekit.framework.core.engine.parts import EnginePart


class Slider(QSlider, EnginePart):
    onValueChangeFunc = None

    def __init__(self):
        super().__init__(orientation=Qt.Orientation.Horizontal)

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

    def setRange(self, start, end):
        super().setRange(start, end)

    def setOrientation(self, orientation):
        orientation = orientation.lower()

        if orientation == "horizontal":
            orient = Qt.Orientation.Horizontal

        elif orientation == "vertical":
            orient = Qt.Orientation.Vertical

        super().setOrientation(orient)

    def setTickPosition(self, position):
        positions = {
            "none": QSlider.TickPosition.NoTicks,
            "above": QSlider.TickPosition.TicksAbove,
            "left": QSlider.TickPosition.TicksLeft,
            "below": QSlider.TickPosition.TicksBelow,
            "right": QSlider.TickPosition.TicksRight,
            "bothsides": QSlider.TickPosition.TicksBothSides,
        }

        super().setTickPosition(positions.get(position) or positions["none"])
