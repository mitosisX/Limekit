import lupa
from PySide6.QtCharts import QBarSet
from limekit.framework.core.engine.parts import EnginePart


class BarSet(QBarSet, EnginePart):
    def __init__(self, title):
        super().__init__(title)

    def addData(self, data):
        self.append(list(data.values()) if lupa.lua_type(data) == "table" else data)
