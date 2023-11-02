import lupa
from PySide6.QtCharts import QBarSeries
from limekit.framework.core.engine.parts import EnginePart


class Bar(QBarSeries, EnginePart):
    name = "BarChart"

    def __init__(self):
        super().__init__()

    def addData(self, data):
        self.append(data)
