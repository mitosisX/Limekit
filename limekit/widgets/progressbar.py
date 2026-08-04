from PySide6.QtWidgets import QProgressBar

from limekit.kernel.coerce import ORIENTATIONS, Enum
from limekit.kernel.spec import Prop
from limekit.widgets.base import LimeWidget, _to_int

_orientation = Enum(ORIENTATIONS, "orientation")


class ProgressBar(LimeWidget, QProgressBar):
    __lime__ = "ui.ProgressBar"

    value = Prop(int, qt=("value", "setValue"))
    orientation = Prop(object, qt=("orientation", "setOrientation"), coerce=_orientation)

    def setRange(self, start, end):
        """Setting the range to (0, 0) makes the bar indeterminate."""
        super().setRange(_to_int(start, "start"), _to_int(end, "end"))
        return self
