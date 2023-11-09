import lupa
from PySide6.QtCharts import QLineSeries
from limekit.framework.core.engine.parts import EnginePart


class Line(QLineSeries, EnginePart):
    name = "LineChart"

    def __init__(self):
        super().__init__()

    # {{x, y}, {x, y}, ...}
    def setData(self, data):
        data = data.values() if lupa.lua_type(data) == "table" else data

        for data_value in data:
            x, y = data_value
            # self.append()
            print(x, " ", y)

    def append(self, x, y):
        super().append(x, y)
