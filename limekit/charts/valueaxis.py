"""A numeric (continuous) chart axis."""

from PySide6.QtCore import QObject

from limekit.charts._qtcharts import HAS_QTCHARTS, QValueAxis, require_charts
from limekit.kernel.declarative import LimeObject
from limekit.kernel.spec import Prop


class ValueAxis(LimeObject, QValueAxis if HAS_QTCHARTS else QObject):
    __lime__ = "chart.ValueAxis"

    titleText = Prop(str, qt=("titleText", "setTitleText"), coerce=str) \
        if HAS_QTCHARTS else None

    def __init__(self):
        require_charts()
        super().__init__()

    def setRange(self, start, end):
        """Qt native re-exposed so it chains like every builder method."""
        super().setRange(start, end)
        return self
