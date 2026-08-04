"""A drop-shadow graphics effect for Lua: `require("limekit.ui").DropShadow`.

Ports `limekit/gui/dropshadow.py` to the 2.0 pattern. `QGraphicsDropShadowEffect`
is a `QObject`, not a `QWidget`, so this is a service-style `LimeObject`.

1.x hardcoded blur=50, colour `#7090B0` at 20% alpha and offset (2, 5) in the
constructor with no way to change any of it afterwards -- and its
constructor body did `self = QGraphicsDropShadowEffect(self)`, rebinding the
local `self` to a second, un-returned effect object while `super().__init__`
had already built the real one; the reassignment was a no-op that quietly
threw away a widget every construction. Those defaults are kept here as
sensible starting values, but each is now a real `Prop` a Lua caller can
read back and override, and there is exactly one effect object.
"""

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect

from limekit.kernel.coerce import Colour
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import Prop


def _to_float(value, label):
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise BridgeError(f"expected a number for {label}, got {value!r}") from exc


def _coerce_blur_radius(value):
    return _to_float(value, "blurRadius")


def _coerce_offset_x(value):
    return _to_float(value, "offsetX")


def _coerce_offset_y(value):
    return _to_float(value, "offsetY")


class DropShadow(LimeObject, QGraphicsDropShadowEffect):
    __lime__ = "ui.DropShadow"

    blurRadius = Prop(float, qt=("blurRadius", "setBlurRadius"),
                       coerce=_coerce_blur_radius,
                       doc="the shadow's blur radius, in pixels")
    color = Prop(object, qt=("color", "setColor"), coerce=Colour)
    offsetX = Prop(float, qt=("xOffset", "setXOffset"), coerce=_coerce_offset_x)
    offsetY = Prop(float, qt=("yOffset", "setYOffset"), coerce=_coerce_offset_y)

    def __init__(self, widget=None):
        super().__init__()
        self.setBlurRadius(50)
        default_colour = QColor("#7090B0")
        default_colour.setAlphaF(0.2)
        self.setColor(default_colour)
        self.setOffset(2, 5)
        if widget is not None:
            self.applyTo(widget)

    def setOffset(self, x, y):
        super().setOffset(_to_float(x, "x"), _to_float(y, "y"))
        return self

    def applyTo(self, widget):
        """Attach this effect to `widget`.

        Qt's `setGraphicsEffect` lives on the widget, not the effect, so
        1.x's constructor-only attachment becomes an explicit, repeatable
        call -- a shadow can be built once and (re)applied to a different
        widget later.
        """
        widget.setGraphicsEffect(self)
        return self
