from PySide6.QtWidgets import QSpinBox
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


class SpinBox(EnginePart, QSpinBox):
    name = "Spinner"
    onValueChangedFunc = None

    def __init__(self):
        super().__init__()
        self.valueChanged.connect(self.__handleValueChange)

    def setOnValueChange(self, onValueChangedFunc):
        self.onValueChangedFunc = onValueChangedFunc

    def __handleValueChange(self):
        if self.onValueChangedFunc:
            self.onValueChangedFunc(self, self.getValue())

    def getValue(self):
        return self.value()
