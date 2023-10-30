from PySide6.QtCore import QDate
from PySide6.QtWidgets import QTimeEdit
from limekit.framework.core.engine.parts import EnginePart


class TimePicker(QTimeEdit, EnginePart):
    timePickedFunc = None

    def __init__(self):
        super().__init__()
        self.setCalendarPopup(True)
        self.editingFinished.connect(self.__handleTimePicked)

    # By pressing "Enter" key
    def setOnTimePicked(self, timePickedFunc):
        self.timePickedFunc = timePickedFunc

    def __handleTimePicked(self):
        if self.timePickedFunc:
            self.timePickedFunc(self, self.getDate())

    def setDate(self, year, month, day):
        self.setDateTime(QDate(year, month, day))

    def getDate(self):
        return self.date().toString("yyyy-M-d")
