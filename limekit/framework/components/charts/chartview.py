from PySide6.QtGui import QPainter
from PySide6.QtCharts import QChartView
from limekit.framework.core.engine.parts import EnginePart


class ChartCanvas(QChartView, EnginePart):
    def __init__(self, chart):
        super().__init__(chart=chart)
        self.setRenderHint(QPainter.Antialiasing)
