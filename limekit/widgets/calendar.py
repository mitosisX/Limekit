"""Calendar date picker.

The 1.x class connected `clicked(QDate)` but handed the *string* through
`getDate()` to its handler rather than the raw `QDate`, so `onDatePicked`
can't use the declarative `Event` spec directly (it wraps `connect` verbatim,
no translation). Hand-written, guarded like every event in this codebase.
"""

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QCalendarWidget

from limekit.kernel.bridge.guard import guard
from limekit.widgets.base import LimeWidget, _to_int


class Calendar(LimeWidget, QCalendarWidget):
    __lime__ = "ui.Calendar"

    def __init__(self):
        super().__init__()
        self._onDatePicked = None
        self.clicked.connect(self._handleDateClicked)

    def setDate(self, year, month, day):
        self.setSelectedDate(QDate(
            _to_int(year, "year"), _to_int(month, "month"), _to_int(day, "day"),
        ))
        return self

    def getDate(self):
        return self.selectedDate().toString("yyyy-M-d")

    def setGridVisible(self, visible):
        """Qt native re-exposed so Lua's `:setGridVisible()` colon syntax works."""
        super().setGridVisible(bool(visible))
        return self

    def isGridVisible(self):
        return super().isGridVisible()

    def setOnDatePicked(self, handler):
        self._onDatePicked = guard(handler, widget="Calendar", event="onDatePicked")
        return self

    def _handleDateClicked(self, date):
        if self._onDatePicked:
            self._onDatePicked(self, self.getDate())
