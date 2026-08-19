"""A repeating or one-shot timer for Lua: `require("limekit.sys").Timer`.

Ports `limekit/core/timer.py` to the 2.0 pattern.

Unit: `interval` stays in **milliseconds**, matching 1.x's `setInterval`
(which passed its argument straight into `QTimer.setInterval` with no
conversion). Lua code that already does `Timer():setInterval(1000):start()`
for a one-second tick keeps working unchanged; silently rescaling to
seconds here would break every demo that builds a timer.
"""

from PySide6.QtCore import QTimer

from limekit.kernel import affinity
from limekit.kernel.bridge.guard import guard
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import Event, Prop


def _to_int(value, label):
    """Duplicated from widgets/base.py: services/ must not import widgets/."""
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise BridgeError(f"expected a number for {label}, got {value!r}") from exc


def _coerce_interval(value):
    return _to_int(value, "interval")


class Timer(LimeObject, QTimer):
    __lime__ = "sys.Timer"

    interval = Prop(int, qt=("interval", "setInterval"), coerce=_coerce_interval,
                     doc="the timer's interval, in milliseconds")
    # Named `single_shot` at the Python/class-attribute level so it does not
    # collide with the `singleShot(msec, callback)` static method below --
    # `lua_name` keeps the Lua-facing accessors (getSingleShot/setSingleShot/
    # isSingleShot) exactly as they'd be if the attribute were named
    # `singleShot` directly.
    single_shot = Prop(bool, qt=("isSingleShot", "setSingleShot"),
                        lua_name="singleShot")

    onTimeout = Event("timeout", passes_self=True,
                       doc="Fired every time the timer fires.")

    def start(self, msec=None):
        """Qt native re-exposed so Lua's `timer:start()` colon syntax works.

        Accepts an optional one-shot interval override, matching
        `QTimer.start(msec)`'s overload, on top of 1.x's no-argument form.

        Registers the timer so shutdown can stop it: a QTimer outlives the
        Lua runtime holding its callback, and one still ticking after
        teardown fires into a dead runtime.
        """
        affinity.register_timer(self)
        if msec is None:
            super().start()
        else:
            super().start(_to_int(msec, "msec"))
        return self

    def stop(self):
        super().stop()
        return self

    def isActive(self):
        return super().isActive()

    @staticmethod
    def singleShot(msec, callback):
        """Fire `callback` once after `msec` milliseconds.

        The callback is guarded like every other Lua-attached handler --
        1.x's static `singleShot` connected the raw Lua function straight
        to `QTimer.singleShot`, so an error inside it would have escaped
        uncaught into the Qt event loop.
        """
        handler = guard(callback, widget="Timer", event="singleShot")
        QTimer.singleShot(_to_int(msec, "msec"), handler)
