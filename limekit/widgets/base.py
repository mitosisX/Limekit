"""Shared widget behaviour, declared once.

Replaces BaseWidget, whose pass-through overrides added nothing and which
half the widget set did not inherit from anyway.
"""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QSizePolicy

from limekit.kernel.coerce import SIZE_POLICIES, Enum
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import Prop

_size_policy = Enum(SIZE_POLICIES, "size policy")


def _to_int(value, label):
    """Coerce to int, translating a raw ValueError/TypeError into BridgeError.

    int("a") raises ValueError, int(None) raises TypeError -- neither is
    something a Lua caller should ever see; every bridge-boundary failure
    must surface as BridgeError.
    """
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise BridgeError(f"expected a number for {label}, got {value!r}") from exc


class LimeWidget(LimeObject):
    """Mixin for every QWidget subclass exposed to Lua."""

    enabled = Prop(bool, qt=("isEnabled", "setEnabled"))
    visible = Prop(bool, qt=("isVisible", "setVisible"))
    toolTip = Prop(str, qt=("toolTip", "setToolTip"), coerce=str)
    styleSheet = Prop(str, qt=("styleSheet", "setStyleSheet"), coerce=str)

    def setResizeRule(self, horizontal, vertical):
        """One definition, seven policies - not three in some widgets."""
        self.setSizePolicy(QSizePolicy(
            _size_policy(horizontal), _size_policy(vertical)
        ))
        return self

    def setSize(self, width, height):
        self.resize(_to_int(width, "width"), _to_int(height, "height"))
        return self

    def setFixedSize(self, width, height):
        super().setFixedSize(QSize(_to_int(width, "width"), _to_int(height, "height")))
        return self

    def setLocation(self, x, y):
        self.move(_to_int(x, "x"), _to_int(y, "y"))
        return self

    def setBackgroundColor(self, colour):
        self.setStyleSheet(f"background-color: {colour};")
        return self
