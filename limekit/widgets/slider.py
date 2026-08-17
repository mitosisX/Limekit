from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSlider

from limekit.kernel.coerce import ORIENTATIONS, Enum
from limekit.kernel.spec import Event, Prop
from limekit.widgets.base import LimeWidget, _to_int

_orientation = Enum(ORIENTATIONS, "orientation")

_TICK_POSITIONS = {
    "none": QSlider.TickPosition.NoTicks,
    "above": QSlider.TickPosition.TicksAbove,
    "left": QSlider.TickPosition.TicksLeft,
    "below": QSlider.TickPosition.TicksBelow,
    "right": QSlider.TickPosition.TicksRight,
    "bothsides": QSlider.TickPosition.TicksBothSides,
}
_tick_position = Enum(_TICK_POSITIONS, "tick position")


class Slider(LimeWidget, QSlider):
    __lime__ = "ui.Slider"

    value = Prop(int, qt=("value", "setValue"))
    orientation = Prop(object, qt=("orientation", "setOrientation"), coerce=_orientation)
    tickPosition = Prop(object, qt=("tickPosition", "setTickPosition"), coerce=_tick_position)

    onValueChange = Event("valueChanged", passes_self=True, params=(("value", "integer"),))

    def __init__(self):
        super().__init__(Qt.Orientation.Horizontal)

    def setRange(self, start, end):
        super().setRange(_to_int(start, "start"), _to_int(end, "end"))
        return self
