from PySide6.QtWidgets import QDial
from limekit.framework.core.engine.parts import EnginePart


class Knob(QDial, EnginePart):
    onValueChangedFunc = None

    def __init__(self):
        super().__init__()
        self.valueChanged.connect(self.__handleValueChanged)

    def __handleValueChanged(self):
        if self.onValueChangedFunc:
            self.onValueChangedFunc(self, self.getValue())

    def setOnValueChanged(self, onValueChangedFunc):
        self.onValueChangedFunc = onValueChangedFunc

    def setRange(self, minimum, maximum):
        super().setRange(minimum, maximum)

    def setValue(self, value):
        super().setValue(value)

    def getValue(self):
        return self.value()

    def setMinValue(self, min_value):
        self.setMinimum(min_value)

    def setMaxValue(self, max_value):
        self.setMaximum(max_value)

    def setIndicators(self, visible):
        self.setNotchesVisible(visible)

    def isIndicatorVisible(self):
        return self.notchesVisible()
