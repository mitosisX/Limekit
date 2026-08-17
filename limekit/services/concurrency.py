"""Threading and cross-thread signalling for Lua: `require("limekit.sys")`.

Ports `limekit/gui/threading.py` (`Thread`) and `limekit/gui/signal.py`
(`QtSignal`) to the 2.0 pattern.

1.x defect not reproduced: `Thread.sleep(self): self.sleep()` -- calling
`thread:sleep()` recursed into itself unconditionally with no base case,
guaranteeing a `RecursionError` (or a hang, on builds with a high recursion
limit) on the very first call, forever. `QThread.sleep(secs)` is a real,
useful *static* method that pauses for a given number of seconds; `sleep`
here calls it properly instead of shadowing it with infinite recursion.
"""

from PySide6.QtCore import QObject, QThread
from PySide6.QtCore import Signal as QtSignal

from limekit.kernel import affinity
from limekit.kernel.bridge.guard import guard
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError


def _to_int(value, label):
    """Coerce to int, translating a raw ValueError/TypeError into BridgeError.

    Duplicated from widgets/base.py rather than imported: services/ must
    not depend on widgets/ (see .importlinter's layering contract).
    """
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise BridgeError(f"expected a number for {label}, got {value!r}") from exc


class Thread(LimeObject, QThread):
    __lime__ = "sys.Thread"

    def __init__(self):
        super().__init__()
        self._onThreadRun = None

    def setOnThreadRun(self, handler):
        self._onThreadRun = guard(handler, widget="Thread", event="onThreadRun")
        return self

    def run(self):
        """Qt virtual override, not a signal -- runs on the worker thread,
        so the handler still crosses guard() the same as every other
        Lua-attached callback."""
        if self._onThreadRun:
            self._onThreadRun(self)

    def start(self):
        # Arms the GUI-thread check on generated setters. Until some worker
        # actually exists there is nothing to catch, so the check stays a
        # single bool test -- see kernel/affinity.py.
        affinity.note_worker_started()
        super().start()
        return self

    def stop(self):
        self.quit()
        return self

    def wait(self, msecs=None):
        if msecs is None:
            super().wait()
        else:
            super().wait(_to_int(msecs, "msecs"))
        return self

    def isRunning(self):
        return super().isRunning()

    def sleep(self, seconds):
        """Pauses the calling thread for `seconds` -- QThread.sleep is a
        static method in Qt; exposed here as an instance method so Lua's
        `thread:sleep(2)` colon syntax works."""
        QThread.sleep(_to_int(seconds, "seconds"))
        return self


class Signal(LimeObject, QObject):
    __lime__ = "sys.Signal"

    # Renamed from the Qt-signal-name-shaped `qt_signal` (1.x) to make clear
    # this is Limekit's OWN class named Signal wrapping ITS OWN QObject
    # signal -- not to be confused with the `PySide6.QtCore.Signal` factory
    # used to declare it, imported above as `QtSignal` to keep the two
    # apart.
    _signal = QtSignal()

    def __init__(self):
        super().__init__()
        self._onSignal = None
        self._signal.connect(self._handleSignal)

    def setOnSignal(self, handler):
        self._onSignal = guard(handler, widget="Signal", event="onSignal")
        return self

    def relay(self):
        """Fires the signal -- safe to call across threads, unlike calling
        a handler directly."""
        self._signal.emit()
        return self

    def _handleSignal(self):
        if self._onSignal:
            self._onSignal(self)
