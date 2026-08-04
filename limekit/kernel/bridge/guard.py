"""The single seam every Lua callback crosses on its way into Python.

Nothing attached through the generated accessors can leak an exception into
the Qt event loop.
"""

import traceback

from limekit.kernel.errors import WidgetCallbackError

_DEFAULT_SINK = None


def _print_sink(error):
    print(f"\n{error}")
    traceback.print_exception(type(error), error, error.__traceback__)


_sink = _print_sink


def set_error_sink(fn):
    """Route guarded errors somewhere (the app's handler, or a test list)."""
    global _sink
    _sink = fn


def reset_error_sink():
    global _sink
    _sink = _print_sink


def guard(fn, *, widget, event):
    """Wrap a callable so it reports rather than raises."""

    def guarded(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:                       # noqa: BLE001
            error = WidgetCallbackError(str(exc), widget=widget, event=event)
            error.__cause__ = exc
            _sink(error)
            return None

    guarded.__name__ = f"guarded_{event}"
    return guarded
