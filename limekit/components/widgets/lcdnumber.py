from PySide6.QtWidgets import QLCDNumber
from limekit.engine.parts import EnginePart


class LCDNumber(QLCDNumber, EnginePart):
    def __init__(self):
        super().__init__()
        self.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)

    def setValuee(self, date):
        self.set

    def getDate(self):
        return self.text()

    # Material properties (classes)
    # danger, warning, success
    def setMatProperty(self, class_):
        self.setProperty("class", class_)
