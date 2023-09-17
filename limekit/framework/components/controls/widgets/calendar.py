from PySide6.QtWidgets import QDateEdit
from limekit.framework.core.engine.parts import EnginePart


class Calendar(QDateEdit, EnginePart):
    dateChangedFuction = None

    def __init__(self):
        super().__init__(calendarPopup=True)
        self.userDateChanged.connect(self.__handleDateChanged)

    def setOnDateChaged(self, dateChangedFunctio):
        self.dateChangedFuction = dateChangedFunctio

    def __handleDateChanged(self, date):
        if self.dateChangedFuction:
            self.dateChangedFuction(self, date.toString("MM/dd/yyyy"))

    def setDate(self, date):
        self.dateTimeFromText(date)

    def getDate(self):
        return self.text()

    # Material properties (classes)
    # danger, warning, success
    def setMatProperty(self, class_):
        self.setProperty("class", class_)
