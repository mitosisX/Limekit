"""A bar series (a collection of `BarSet`s)."""

from PySide6.QtCore import QObject

from limekit.charts._qtcharts import HAS_QTCHARTS, QBarSeries, require_charts
from limekit.kernel.declarative import LimeObject


class BarChart(LimeObject, QBarSeries if HAS_QTCHARTS else QObject):
    __lime__ = "chart.BarChart"

    def __init__(self):
        require_charts()
        super().__init__()

    def append(self, barset):
        """Qt native re-exposed so it chains like every builder method."""
        super().append(barset)
        return self

    def attachAxis(self, axis):
        super().attachAxis(axis)
        return self
