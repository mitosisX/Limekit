from PySide6.QtWidgets import QDial
from limekit.framework.core.engine.parts import EnginePart


class Knob(QDial, EnginePart):
    onValueChangedFunc = None

    def __init__(self):
        super().__init__()
        self.valueChanged.connect(self.__handleValueChanged)

    def setOnValueChanged(self, onValueChangedFunc):
        self.onValueChangedFunc = onValueChangedFunc

    def __handleValueChanged(self):
        if self.onValueChangedFunc:
            self.onValueChangedFunc(self, self.getValue())

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

    def hasIndicators(self):
        return self.notchesVisible()
