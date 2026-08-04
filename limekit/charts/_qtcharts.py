"""Guards every chart module against a PySide6 build without QtCharts.

PySide6 ships Charts as an optional add-on; some distributions omit it. Every
class in `limekit/charts/` imports its Qt base from here instead of
`PySide6.QtCharts` directly, so a missing add-on degrades to a clear
`BridgeError` raised the moment a chart class is *used* (instantiated),
rather than an `ImportError` at collection time that would take every other
`limekit.charts.*` module -- and the whole manifest/test collection -- down
with it.

Confirmed in this environment: `PySide6.QtCharts` imports successfully
(see the Phase D report for the verification command and its output).
"""

try:
    from PySide6.QtCharts import (
        QAreaSeries,
        QBarCategoryAxis,
        QBarSeries,
        QBarSet,
        QChart,
        QChartView,
        QLineSeries,
        QValueAxis,
    )
    HAS_QTCHARTS = True
except ImportError:
    HAS_QTCHARTS = False
    QAreaSeries = QBarCategoryAxis = QBarSeries = QBarSet = None
    QChart = QChartView = QLineSeries = QValueAxis = None


def require_charts():
    if not HAS_QTCHARTS:
        from limekit.kernel.errors import BridgeError
        raise BridgeError(
            "PySide6.QtCharts is not available in this environment; "
            "charts are disabled in this build"
        )
