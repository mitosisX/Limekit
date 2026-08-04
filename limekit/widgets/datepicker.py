"""Date picker (drop-down calendar popup).

Like Calendar, `onDatePick` hands the handler a formatted string rather than
the raw `QDateTime` the underlying `userDateChanged` signal carries, so it is
hand-written and guarded rather than a declarative `Event`.
"""

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QDateEdit

from limekit.kernel.bridge.guard import guard
from limekit.widgets.base import LimeWidget, _to_int


class DatePicker(LimeWidget, QDateEdit):
    __lime__ = "ui.DatePicker"

    def __init__(self):
        super().__init__(calendarPopup=True)
        self._onDatePick = None
        self.userDateChanged.connect(self._handleDatePicked)

    def setDate(self, year, month, day):
        """1.x defects not reproduced: `QDateTime(year, month, day, hour,
        minutes)` -- a 5-int-argument overload PySide's QDateTime does not
        have -- raised a raw TypeError on every call. Even fixed to build a
        proper QDateTime and call setDateTime() with it, PySide6's QDateEdit
        silently rolls the displayed date back a day on some datetime/locale
        combinations (verified against this Qt build). QDateEdit only ever
        displays a date, never a time, so the `hour`/`minutes` 1.x accepted
        were never shown anyway; going through the real Qt native
        `setDate(QDate)` sidesteps the QDateTime round-trip bug entirely."""
        super().setDate(QDate(
            _to_int(year, "year"), _to_int(month, "month"), _to_int(day, "day"),
        ))
        return self

    def getDate(self):
        return self.date().toString("yyyy-M-d")

    def setOnDatePick(self, handler):
        self._onDatePick = guard(handler, widget="DatePicker", event="onDatePick")
        return self

    def _handleDatePicked(self, _qdate):
        if self._onDatePick:
            self._onDatePick(self, self.getDate())
