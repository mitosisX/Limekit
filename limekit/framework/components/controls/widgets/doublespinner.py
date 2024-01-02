from PySide6.QtWidgets import QDoubleSpinBox
from limekit.framework.core.engine.parts import EnginePart

"""_summary_

def cleanText()
def displayIntegerBase()
def maximum()
def minimum()
def prefix()
def setDisplayIntegerBase(base)
def setMaximum(max)
def setMinimum(min)
def setPrefix(prefix)
def setRange(min, max)
def setSingleStep(val)
def setStepType(stepType)
def setSuffix(suffix)
def singleStep()
def stepType()
def suffix()
def value()
"""


class DoubleSpinBox(QDoubleSpinBox, EnginePart):
    name = "DoubleSpinner"
    onValueChangedFunc = None

    def __init__(self):
        super().__init__()
        self.valueChanged.connect(self.__handleValueChange)

    def __handleValueChange(self):
        if self.onValueChangedFunc:
            self.onValueChangedFunc(self, self.getValue())

    def setOnValueChange(self, onValueChangedFunc):
        self.onValueChangedFunc = onValueChangedFunc

    def setPrefix(self, prefix):
        super().setPrefix(prefix)

    def setSuffix(self, suffix):
        super().setSuffix(suffix)

    def setValue(self, value):
        super().setValue(value)

    def setRange(self, start, end):
        super().setRange(start, end)

    def getValue(self):
        return self.value()
