from PySide6.QtGui import QPainter
from PySide6.QtCharts import QChartView, QChart
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.handle.scripts.swissknife.converters import Converter


class ChartCanvas(QChartView, EnginePart):
    def __init__(self, chart):
        super().__init__(chart=chart)
        self.setRenderHint(QPainter.Antialiasing)

    def setTheme(self, theme):
        theme = theme.lower()

        themes = {
            "light": QChart.ChartTheme.ChartThemeLight,
            "dark": QChart.ChartTheme.ChartThemeDark,
            "qt": QChart.ChartTheme.ChartThemeQt,
            "bluecerulean": QChart.ChartTheme.ChartThemeBlueCerulean,
            "brownsand": QChart.ChartTheme.ChartThemeBrownSand,
            "bluencs": QChart.ChartTheme.ChartThemeBlueNcs,
            "highconstrast": QChart.ChartTheme.ChartThemeHighContrast,
            "blueicy": QChart.ChartTheme.ChartThemeBlueIcy,
        }

        self.chart().setTheme(themes[theme] if themes.get(theme) else theme["light"])

    def getThemes(self):
        return Converter.table_from(
            [
                "light",
                "dark",
                "qt",
                "bluecerulean",
                "brownsand",
                "bluencs",
                "highconstrast",
                "blueicy",
            ]
        )
