"""A plain QWidget used to hold a layout or a single child.

`onKeyPress` overrides a Qt virtual method rather than wrapping a signal, so
it cannot use the declarative `Event` spec (which wraps `connect`) - the same
situation as Window's events. It is hand-written but still crosses `guard()`.
"""

from PySide6.QtCore import Qt
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

    @staticmethod
    def _key_name(code):
        """"Escape", "Return", "A" -- not Qt's "Key_Escape" and not an int.

        Handing the raw QKeyEvent to Lua looked reasonable but was useless
        there: its accessors are Qt-native, so `event:text()` passes the
        event twice and raises, and `tostring(event)` prints a Shiboken
        repr. Window's mouse events already pass plain x and y for the same
        reason.
        """
        try:
            name = Qt.Key(code).name
        except ValueError:
            return str(code)
        return name[4:] if name.startswith("Key_") else name

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
            self._onKeyPress(self, self._key_name(event.key()), event.text())
        super().keyPressEvent(event)
