import lupa
from PySide6.QtCharts import QBarSet
from limekit.engine.parts import EnginePart


class BarSet(QBarSet, EnginePart):
    def __init__(self, title):
        super().__init__(title)

    def append(self, data):
        super().append(list(data.values()) if lupa.lua_type(data) == "table" else data)
