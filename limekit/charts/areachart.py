"""A filled area between two line series.

1.x defect not reproduced: `AreaChart.__init__` called `QAreaSeries(title)`
-- but `QAreaSeries` has no string-taking constructor overload, only
`QAreaSeries()`, `QAreaSeries(upper)` and `QAreaSeries(upper, lower)`; the
1.x constructor would raise a `TypeError` from PySide the instant a Lua
script ever called `AreaChart("title")`, and `append`, which 1.x also
declared, does not exist on `QAreaSeries` at all -- only `QLineSeries` has
it. This takes the upper/lower `LineChart` series `QAreaSeries` actually
wants and exposes `name`/`append` only where the real Qt API has them.
"""

from PySide6.QtCore import QObject

from limekit.charts._qtcharts import HAS_QTCHARTS, QAreaSeries, require_charts
from limekit.kernel.declarative import LimeObject
from limekit.kernel.spec import Prop


class AreaChart(LimeObject, QAreaSeries if HAS_QTCHARTS else QObject):
    __lime__ = "chart.AreaChart"

    name = Prop(str, qt=("name", "setName"), coerce=str) if HAS_QTCHARTS else None

    def __init__(self, upper, lower=None):
        require_charts()
        if lower is not None:
            super().__init__(upper, lower)
        else:
            super().__init__(upper)
