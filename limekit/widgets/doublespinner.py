from PySide6.QtWidgets import QDoubleSpinBox

from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import Event, Prop
from limekit.widgets.base import LimeWidget


def _to_float(value, label):
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise BridgeError(f"expected a number for {label}, got {value!r}") from exc


class DoubleSpinner(LimeWidget, QDoubleSpinBox):
    __lime__ = "ui.DoubleSpinner"

    value = Prop(float, qt=("value", "setValue"))
    prefix = Prop(str, qt=("prefix", "setPrefix"), coerce=str)
    suffix = Prop(str, qt=("suffix", "setSuffix"), coerce=str)

    onValueChange = Event("valueChanged", passes_self=True, params=(("value", "number"),))

    def setRange(self, start, end):
        super().setRange(_to_float(start, "start"), _to_float(end, "end"))
        return self
