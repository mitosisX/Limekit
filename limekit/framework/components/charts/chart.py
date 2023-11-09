import lupa
from PySide6.QtCharts import QChart
from PySide6.QtCore import Qt
from limekit.framework.core.engine.parts import EnginePart


"""
2 November, 2023 (4:56 PM) (Wednesday)
"""


class Chart(QChart, EnginePart):
    @lupa.unpacks_lua_table
    def __init__(self, kwargs):
        super().__init__()

        if "title" in kwargs:
            self.setTitle(kwargs["title"])

        if "animation" in kwargs:
            self.setAnimation(kwargs["animation"])

    def __decideAnimation(self, animation):
        animation = animation.lower()

        animation_type = Chart.AnimationOption.NoAnimation

        match (animation):
            case (None):
                animation_type = Chart.AnimationOption.NoAnimation
            case ("series"):
                animation_type = Chart.AnimationOption.SeriesAnimations
            case ("grid"):
                animation_type = Chart.AnimationOption.GridAxisAnimations
            case ("all"):
                animation_type = Chart.AnimationOption.AllAnimations

        self.setAnimationOptions(animation_type)

    def setAnimation(self, animation):
        self.__decideAnimation(animation)

    def setTitle(self, title):
        super().setTitle(title)

    def addSeries(self, chart_type):
        super().addSeries(chart_type)

    def addAxis(self, axis, position):
        positions = {
            "left": Qt.AlignLeft,
            "top": Qt.AlignTop,
            "right": Qt.AlignRight,
            "bottom": Qt.AlignBottom,
        }
        super().addAxis(
            axis, positions[position] if positions.get(position) else positions["top"]
        )

    def setLegendVisibility(self, visibility):
        self.legend().setVisible(visibility)

    def setLegendAlignment(self, position):
        positions = {
            "left": Qt.AlignLeft,
            "right": Qt.AlignRight,
            "bottom": Qt.AlignBottom,
            "top": Qt.AlignTop,
        }
        self.legend().setAlignment(
            positions[position] if positions.get(position) else positions["bottom"]
        )
