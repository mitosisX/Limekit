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
        """Notify the handler, then let Qt process the key as normal.

        This used to call `super()` only in the `else` branch, so attaching an
        `onKeyPress` handler silently switched off default key handling for
        everything inside the Container -- most visibly, text widgets stopped
        receiving input. Observing a key is not the same as consuming it, so
        the handler runs and Qt still gets its turn. `Window` already does it
        in this order.
        """
        if self._onKeyPress:
            self._onKeyPress(self, event)
        super().keyPressEvent(event)
