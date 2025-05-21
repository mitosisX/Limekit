import lupa
from PySide6.QtCharts import QBarSeries
from limekit.engine.parts import EnginePart


class Bar(QBarSeries, EnginePart):
    name = "BarChart"

    def __init__(self):
        super().__init__()

    def append(self, data):
        super().append(data)

    def attachAxis(self, axis):
        super().attachAxis(axis)
