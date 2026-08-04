"""A single dividing line (QFrame in HLine/VLine shape).

1.x defect not reproduced: an unknown orientation raised a raw `ValueError`
instead of a `BridgeError` -- every failure crossing the Lua bridge must be a
`BridgeError` (see kernel/coerce.py's `Enum`, which this now reuses instead
of a hand-rolled if/elif/raise).
"""

from PySide6.QtWidgets import QFrame

from limekit.kernel.coerce import Enum
from limekit.widgets.base import LimeWidget

_SHAPES = {
    "horizontal": QFrame.Shape.HLine,
    "vertical": QFrame.Shape.VLine,
}
_shape = Enum(_SHAPES, "orientation")


class Separator(LimeWidget, QFrame):
    __lime__ = "ui.Separator"

    def __init__(self, orientation="horizontal"):
        super().__init__()
        self.setFrameShape(_shape(orientation))
        self.setLineWidth(1)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setMidLineWidth(0)
