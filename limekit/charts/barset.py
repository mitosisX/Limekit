"""One named set of bar values within a BarChart."""

from PySide6.QtCore import QObject

from limekit.charts._qtcharts import HAS_QTCHARTS, QBarSet, require_charts
from limekit.kernel.bridge.convert import as_sequence
from limekit.kernel.declarative import LimeObject
from limekit.kernel.spec import Prop


class BarSet(LimeObject, QBarSet if HAS_QTCHARTS else QObject):
    __lime__ = "chart.BarSet"

    label = Prop(str, qt=("label", "setLabel"), coerce=str) if HAS_QTCHARTS else None

    def __init__(self, title=""):
        require_charts()
        super().__init__(str(title))

    def append(self, values):
        """Accepts a Lua table or Python sequence of numbers."""
        super().append(list(as_sequence(values)))
        return self
