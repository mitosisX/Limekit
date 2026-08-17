from PySide6.QtWidgets import QSpinBox

from limekit.kernel.spec import Event, Prop
from limekit.widgets.base import LimeWidget, _to_int


class Spinner(LimeWidget, QSpinBox):
    __lime__ = "ui.Spinner"

    value = Prop(int, qt=("value", "setValue"))
    prefix = Prop(str, qt=("prefix", "setPrefix"), coerce=str)
    suffix = Prop(str, qt=("suffix", "setSuffix"), coerce=str)

    onValueChange = Event("valueChanged", passes_self=True, params=(("value", "integer"),))

    def setRange(self, start, end):
        super().setRange(_to_int(start, "start"), _to_int(end, "end"))
        return self
