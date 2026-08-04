"""Shared widget behaviour, declared once.

Replaces BaseWidget, whose pass-through overrides added nothing and which
half the widget set did not inherit from anyway.
"""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QSizePolicy

from limekit.kernel.coerce import SIZE_POLICIES, Enum
from limekit.kernel.declarative import LimeObject
from limekit.kernel.spec import Prop

_size_policy = Enum(SIZE_POLICIES, "size policy")


class LimeWidget(LimeObject):
    """Mixin for every QWidget subclass exposed to Lua."""

    enabled = Prop(bool, default=True, qt=("isEnabled", "setEnabled"))
    visible = Prop(bool, default=True, qt=("isVisible", "setVisible"))
    toolTip = Prop(str, default="", qt=("toolTip", "setToolTip"), coerce=str)
    styleSheet = Prop(str, default="", qt=("styleSheet", "setStyleSheet"), coerce=str)

    def setResizeRule(self, horizontal, vertical):
        """One definition, seven policies - not three in some widgets."""
        self.setSizePolicy(QSizePolicy(
            _size_policy(horizontal), _size_policy(vertical)
        ))
        return self

    def setSize(self, width, height):
        self.resize(int(width), int(height))
        return self

    def setFixedSize(self, width, height):
        super().setFixedSize(QSize(int(width), int(height)))
        return self

    def setLocation(self, x, y):
        self.move(int(x), int(y))
        return self

    def setBackgroundColor(self, colour):
        self.setStyleSheet(f"background-color: {colour};")
        return self
