"""Rotary dial input."""

from PySide6.QtWidgets import QDial

from limekit.kernel.spec import Event, Prop
from limekit.widgets.base import LimeWidget, _to_int


class Knob(LimeWidget, QDial):
    __lime__ = "ui.Knob"

    value = Prop(int, qt=("value", "setValue"))
    notchesVisible = Prop(bool, qt=("notchesVisible", "setNotchesVisible"))

    onValueChanged = Event("valueChanged", passes_self=True)

    def __init__(self):
        super().__init__()

    def setRange(self, minimum, maximum):
        super().setRange(_to_int(minimum, "minimum"), _to_int(maximum, "maximum"))
        return self

    def setMinValue(self, minimum):
        self.setMinimum(_to_int(minimum, "minimum"))
        return self

    def setMaxValue(self, maximum):
        self.setMaximum(_to_int(maximum, "maximum"))
        return self
