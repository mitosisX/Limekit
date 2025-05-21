import lupa
from limekit.engine.parts import EnginePart
from PySide6.QtCharts import QBarCategoryAxis


class CategoryAxis(QBarCategoryAxis, EnginePart):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.append(data)

    def append(self, data):
        super().append(data.values() if lupa.lua_type(data) == "table" else data)
