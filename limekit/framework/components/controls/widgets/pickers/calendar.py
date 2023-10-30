from PySide6.QtCore import QDate
from PySide6.QtWidgets import QCalendarWidget
from limekit.framework.core.engine.parts import EnginePart


class Calendar(QCalendarWidget, EnginePart):
    datePickedFunc = None

    def __init__(self):
        super().__init__()
        self.clicked.connect(self.__handleDateChanged)

    def setOnDatePicked(self, datePickedFunc):
        self.datePickedFunc = datePickedFunc

    def __handleDateChanged(self):
        if self.datePickedFunc:
            self.datePickedFunc(self, self.getDate())

    def setDate(self, year, month, day):
        self.setSelectedDate(QDate(year, month, day))

    def getDate(self):
        return self.selectedDate().toString("yyyy-M-d")
