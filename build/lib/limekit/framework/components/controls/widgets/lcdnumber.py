from PySide6.QtWidgets import QLCDNumber
from limekit.framework.core.engine.parts import EnginePart


class LCDNumber(EnginePart, QLCDNumber):
    def __init__(self):
        super().__init__()

    def onClick(self, func):
        self.clicked.connect(lambda: func(self))

    def setDate(self, date):
        self.dateTimeFromText(date)

    def getDate(self):
        return self.text()

    # Material properties (classes)
    # danger, warning, success
    def setMatProperty(self, class_):
        self.setProperty("class", class_)
