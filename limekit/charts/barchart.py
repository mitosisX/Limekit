"""Bar series -- grouped, stacked, percentage, and horizontal.

Qt has one bar series per arrangement (`QBarSeries`, `QStackedBarSeries`,
`QPercentBarSeries`, `QHorizontalBarSeries`), all sharing
`QAbstractBarSeries`'s API. They are exposed as four classes here for the
same reason Qt has four: the arrangement is decided when the series is
created, not toggled afterwards, so a `setStacked(true)` would be lying
about what the object can do.

Everything they share -- `append`, `attachAxis`, the label controls -- lives
on `_BarSeries`, which carries no `__lime__` of its own and so is not
registered. Only the four concrete classes reach Lua.
"""

from PySide6.QtCore import QObject

from limekit.charts._qtcharts import (
    HAS_QTCHARTS,
    QBarSeries,
    QHorizontalBarSeries,
    QPercentBarSeries,
    QStackedBarSeries,
    require_charts,
)
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError

_LABEL_POSITIONS = {
    "center": "LabelsCenter",
    "insideend": "LabelsInsideEnd",
    "insidebase": "LabelsInsideBase",
    "outsideend": "LabelsOutsideEnd",
}


class _BarSeries(LimeObject):
    """The API every bar arrangement shares. Not registered on its own."""

    def append(self, barset):
        """Qt native re-exposed so it chains like every builder method."""
        super().append(barset)
        return self

    def attachAxis(self, axis):
        super().attachAxis(axis)
        return self

    def setBarWidth(self, width):
        """How much of each category slot the bars fill, from 0 to 1."""
        super().setBarWidth(float(width))
        return self

    def setLabelsVisible(self, visible=True):
        """Draws each bar's value on it -- the point of a percentage chart."""
        super().setLabelsVisible(bool(visible))
        return self

    def setLabelsFormat(self, text):
        """A format string for those labels, where @value is the number."""
        super().setLabelsFormat(str(text))
        return self

    def setLabelsPosition(self, position):
        """One of: center, insideend, insidebase, outsideend."""
        if not isinstance(position, str) or position.lower() not in _LABEL_POSITIONS:
            raise BridgeError(
                f"unknown label position {position!r}; expected one of: "
                f"{', '.join(sorted(_LABEL_POSITIONS))}"
            )
        attribute = _LABEL_POSITIONS[position.lower()]
        super().setLabelsPosition(getattr(type(self).LabelsPosition, attribute))
        return self


class BarChart(_BarSeries, QBarSeries if HAS_QTCHARTS else QObject):
    """Bars for each set side by side within a category."""

    __lime__ = "chart.BarChart"

    def __init__(self):
        require_charts()
        super().__init__()


class StackedBarChart(_BarSeries, QStackedBarSeries if HAS_QTCHARTS else QObject):
    """Bars for each set piled on top of each other, so the bar's height is
    the total. Use it when the total matters as much as the parts."""

    __lime__ = "chart.StackedBarChart"

    def __init__(self):
        require_charts()
        super().__init__()


class PercentBarChart(_BarSeries, QPercentBarSeries if HAS_QTCHARTS else QObject):
    """Stacked, but every bar is scaled to the full height, so what you read
    is each set's share rather than its size."""

    __lime__ = "chart.PercentBarChart"

    def __init__(self):
        require_charts()
        super().__init__()


class HorizontalBarChart(_BarSeries, QHorizontalBarSeries if HAS_QTCHARTS else QObject):
    """Bars running left to right. Worth reaching for when the category
    labels are long, since they get a whole row each instead of being
    squeezed under a column.

    The axes swap round with the bars: the CategoryAxis goes on the left and
    the ValueAxis along the bottom."""

    __lime__ = "chart.HorizontalBarChart"

    def __init__(self):
        require_charts()
        super().__init__()
