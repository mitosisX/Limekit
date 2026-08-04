"""Seven-segment numeric display.

1.x defect not reproduced: `setValuee` (misspelled) had a body of `self.set`
-- a bare attribute reference, not even a call, so the method was
unconditionally broken and unreachable (nothing else in the 1.x codebase
called the misspelled name either). `setValue`/`getValue` here are real.
"""

from PySide6.QtWidgets import QLCDNumber

from limekit.kernel.coerce import Enum
from limekit.kernel.spec import Prop
from limekit.widgets.base import LimeWidget

_SEGMENT_STYLES = {
    "outline": QLCDNumber.SegmentStyle.Outline,
    "filled": QLCDNumber.SegmentStyle.Filled,
    "flat": QLCDNumber.SegmentStyle.Flat,
}
_segment_style = Enum(_SEGMENT_STYLES, "segment style")


class LCDNumber(LimeWidget, QLCDNumber):
    __lime__ = "ui.LCDNumber"

    digitCount = Prop(int, qt=("digitCount", "setDigitCount"))
    segmentStyle = Prop(object, qt=("segmentStyle", "setSegmentStyle"),
                         coerce=_segment_style)

    def __init__(self):
        super().__init__()
        self.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)

    def setValue(self, value):
        """QLCDNumber has no real setValue; `display()` is the Qt native."""
        self.display(value)
        return self

    def getValue(self):
        return self.value()

    def setMatProperty(self, class_):
        """Attaches a stylesheet class, e.g. "danger"/"warning"/"success"."""
        self.setProperty("class", str(class_))
        return self
