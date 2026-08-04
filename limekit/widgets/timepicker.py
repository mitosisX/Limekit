"""Time picker.

1.x defect not reproduced: `setDate(self, year, month, day):
self.setDateTime(QDate(year, month, day))` fed a `QDate` (no time component)
into `QTimeEdit.setDateTime`, which expects a `QDateTime` -- on a widget that
only ever displays a time. That never worked; this exposes `setTime`/`getTime`
against `QTime` instead, which is what a `QTimeEdit` actually holds.
"""

from PySide6.QtCore import QTime
from PySide6.QtWidgets import QTimeEdit

from limekit.kernel.bridge.guard import guard
from limekit.widgets.base import LimeWidget, _to_int


class TimePicker(LimeWidget, QTimeEdit):
    __lime__ = "ui.TimePicker"

    def __init__(self):
        super().__init__()
        self._onTimePicked = None
        self.setCalendarPopup(True)
        self.editingFinished.connect(self._handleTimePicked)

    def setTime(self, hour, minute, second=0):
        """Overrides QTimeEdit.setTime(QTime) directly -- same name, a
        friendlier Lua-facing signature, exactly how TextField.setText
        overrides QTextEdit.setText."""
        super().setTime(QTime(
            _to_int(hour, "hour"), _to_int(minute, "minute"), _to_int(second, "second"),
        ))
        return self

    def getTime(self):
        return self.time().toString("H:m:s")

    def setOnTimePicked(self, handler):
        """Fires on Enter (Qt's `editingFinished`), matching the 1.x comment."""
        self._onTimePicked = guard(handler, widget="TimePicker", event="onTimePicked")
        return self

    def _handleTimePicked(self):
        if self._onTimePicked:
            self._onTimePicked(self, self.getTime())
