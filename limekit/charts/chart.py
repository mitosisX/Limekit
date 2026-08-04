"""The chart canvas that series/axes attach to."""

from PySide6.QtCore import QObject, Qt

from limekit.charts._qtcharts import HAS_QTCHARTS, QChart, require_charts
from limekit.kernel.bridge.convert import as_mapping
from limekit.kernel.coerce import Enum
from limekit.kernel.declarative import LimeObject
from limekit.kernel.spec import Prop

_ANIMATIONS = {
    "none": QChart.AnimationOption.NoAnimation if HAS_QTCHARTS else None,
    "series": QChart.AnimationOption.SeriesAnimations if HAS_QTCHARTS else None,
    "grid": QChart.AnimationOption.GridAxisAnimations if HAS_QTCHARTS else None,
    "all": QChart.AnimationOption.AllAnimations if HAS_QTCHARTS else None,
}
_animation = Enum(_ANIMATIONS, "animation")

_ALIGNMENTS = {
    "left": Qt.AlignmentFlag.AlignLeft,
    "top": Qt.AlignmentFlag.AlignTop,
    "right": Qt.AlignmentFlag.AlignRight,
    "bottom": Qt.AlignmentFlag.AlignBottom,
}
_alignment = Enum(_ALIGNMENTS, "chart alignment")


class Chart(LimeObject, QChart if HAS_QTCHARTS else QObject):
    __lime__ = "chart.Chart"

    title = Prop(str, qt=("title", "setTitle"), coerce=str) if HAS_QTCHARTS else None

    def __init__(self, options=None, **kwargs):
        require_charts()
        super().__init__()
        options = as_mapping(options)
        options.update(kwargs)

        if "title" in options:
            self.setTitle(str(options["title"]))
        if "animation" in options:
            self.setAnimation(options["animation"])

    def setAnimation(self, animation):
        self.setAnimationOptions(_animation(animation))
        return self

    def addSeries(self, series):
        """Qt native re-exposed so it chains like every builder method."""
        super().addSeries(series)
        return self

    def addAxis(self, axis, position="top"):
        super().addAxis(axis, _alignment(position))
        return self

    def setLegendVisibility(self, visible):
        self.legend().setVisible(bool(visible))
        return self

    def setLegendAlignment(self, position="bottom"):
        self.legend().setAlignment(_alignment(position))
        return self
