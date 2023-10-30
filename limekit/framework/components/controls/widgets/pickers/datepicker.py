from PySide6.QtWidgets import QDateEdit
from PySide6.QtCore import QDateTime, QDate
from limekit.framework.core.engine.parts import EnginePart


class DatePicker(QDateEdit, EnginePart):
    datePickedFunc = None

    def __init__(self):
        super().__init__(calendarPopup=True)
        self.userDateChanged.connect(self.__handleDatePicked)

    def setOnDatePicked(self, datePickedFunc):
        self.datePickedFunc = datePickedFunc

    def __handleDatePicked(self):
        if self.datePickedFunc:
            self.datePickedFunc(self, self.getDate())

    def setDate(self, year, month, day, hour, minutes):
        self.setDateTime(QDateTime(year, month, day, hour, minutes))

    def getDate(self):
        return self.date().toString("yyyy-M-d")
