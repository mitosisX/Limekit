"""A line series.

1.x defect not reproduced: `setData` iterated the given points and
`print(x, " ", y)`-ed them instead of ever calling `append` -- passing data
to `setData` silently drew nothing. `setData` here actually appends.
"""

from PySide6.QtCore import QObject

from limekit.charts._qtcharts import HAS_QTCHARTS, QLineSeries, require_charts
from limekit.kernel.bridge.convert import as_sequence
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import Prop


class LineChart(LimeObject, QLineSeries if HAS_QTCHARTS else QObject):
    __lime__ = "chart.LineChart"

    name = Prop(str, qt=("name", "setName"), coerce=str) if HAS_QTCHARTS else None

    def __init__(self):
        require_charts()
        super().__init__()

    def append(self, x, y):
        """Qt native re-exposed so it chains like every builder method."""
        super().append(x, y)
        return self

    def setData(self, points):
        """Accepts a Lua table or Python sequence of {x, y} pairs."""
        for point in as_sequence(points):
            values = as_sequence(point)
            if len(values) != 2:
                raise BridgeError(f"expected an {{x, y}} pair, got {point!r}")
            self.append(*values)
        return self
