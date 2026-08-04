"""A categorical (labelled) chart axis, e.g. bar-chart category labels."""

from PySide6.QtCore import QObject

from limekit.charts._qtcharts import HAS_QTCHARTS, QBarCategoryAxis, require_charts
from limekit.kernel.bridge.convert import as_sequence
from limekit.kernel.declarative import LimeObject


class CategoryAxis(LimeObject, QBarCategoryAxis if HAS_QTCHARTS else QObject):
    __lime__ = "chart.CategoryAxis"

    def __init__(self, categories=None):
        require_charts()
        super().__init__()
        if categories is not None:
            self.append(categories)

    def append(self, categories):
        """Accepts a Lua table or Python sequence of category labels."""
        super().append([str(c) for c in as_sequence(categories)])
        return self
