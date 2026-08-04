"""A plain QWidget used to hold a layout or a single child.

`onKeyPress` overrides a Qt virtual method rather than wrapping a signal, so
it cannot use the declarative `Event` spec (which wraps `connect`) - the same
situation as Window's events. It is hand-written but still crosses `guard()`.
"""

from PySide6.QtWidgets import QWidget

from limekit.kernel.bridge.guard import guard
from limekit.kernel.spec import Prop
from limekit.widgets.base import LimeWidget


class Container(LimeWidget, QWidget):
    __lime__ = "ui.Container"

    layout = Prop(object, qt=("layout", "setLayout"))

    def __init__(self, parent=None):
        super().__init__(parent)
        self._onKeyPress = None

    def setOnKeyPress(self, handler):
        self._onKeyPress = guard(handler, widget="Container", event="onKeyPress")
        return self

    def keyPressEvent(self, event):
        if self._onKeyPress:
            self._onKeyPress(self, event)
        else:
            super().keyPressEvent(event)
