from PySide6.QtCharts import QValueAxis
from limekit.engine.parts import EnginePart


class ValueAxis(QValueAxis, EnginePart):
    def __init__(self):
        super().__init__()

    def setRange(self, start, end):
        super().setRange(start, end)
