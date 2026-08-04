"""The widget that actually draws a Chart. `QChartView` is a real `QWidget`,
unlike `Chart`/`LineChart`/etc, so this is the one chart class that uses
`LimeWidget` rather than plain `LimeObject`.
"""

from PySide6.QtCore import QObject
from PySide6.QtGui import QPainter

from limekit.charts._qtcharts import HAS_QTCHARTS, QChart, QChartView, require_charts
from limekit.kernel.bridge.convert import to_lua
from limekit.kernel.coerce import Enum
from limekit.kernel.spec import Prop
from limekit.widgets.base import LimeWidget

_THEMES = {
    "light": QChart.ChartTheme.ChartThemeLight if HAS_QTCHARTS else None,
    "dark": QChart.ChartTheme.ChartThemeDark if HAS_QTCHARTS else None,
    "qt": QChart.ChartTheme.ChartThemeQt if HAS_QTCHARTS else None,
    "bluecerulean": QChart.ChartTheme.ChartThemeBlueCerulean if HAS_QTCHARTS else None,
    "brownsand": QChart.ChartTheme.ChartThemeBrownSand if HAS_QTCHARTS else None,
    "bluencs": QChart.ChartTheme.ChartThemeBlueNcs if HAS_QTCHARTS else None,
    "highcontrast": QChart.ChartTheme.ChartThemeHighContrast if HAS_QTCHARTS else None,
    "blueicy": QChart.ChartTheme.ChartThemeBlueIcy if HAS_QTCHARTS else None,
}
_theme = Enum(_THEMES, "chart theme")


class ChartView(LimeWidget, QChartView if HAS_QTCHARTS else QObject):
    __lime__ = "chart.ChartView"

    chart = Prop(object, qt=("chart", "setChart")) if HAS_QTCHARTS else None

    def __init__(self, chart=None):
        require_charts()
        if chart is not None:
            super().__init__(chart=chart)
        else:
            super().__init__()
        self.setRenderHint(QPainter.RenderHint.Antialiasing)

    def setTheme(self, theme):
        self.chart().setTheme(_theme(theme))
        return self

    def getThemes(self):
        return to_lua(sorted(_THEMES))
