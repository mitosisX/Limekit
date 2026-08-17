"""Catching widget access from a worker thread.

Qt widgets belong to the thread that created them -- the GUI thread -- and
touching one from anywhere else is undefined behaviour. Not an exception: a
crash, or silent corruption, at some unrelated point later.

`sys.Thread` makes that mistake easy to reach and gives no warning:

    local worker = sys.Thread()
    worker:setOnThreadRun(function()
        label:setText("done")        -- wrong thread; may take the app down
    end)
    worker:start()

The handler itself is legitimately off-thread; what is not legitimate is
touching a widget inside it. So the check belongs where Lua actually reaches
a widget -- the generated setters -- not on the callback.

Cost: a module-global bool test per setter call, which is nothing. The real
check (asking Qt for the current thread) only runs once a worker thread has
actually been started, so an app that never uses `sys.Thread` never pays for
it at all.

The correct fix for a Lua author who trips this is `sys.Signal`: fire it from
the thread, update widgets in its handler, which runs on the GUI thread.
"""

from PySide6.QtCore import QThread

from limekit.kernel.errors import BridgeError

_gui_thread = None
_workers_started = False


def set_gui_thread(thread=None):
    """Record the thread widgets belong to. Called by `LimekitApp.boot()`."""
    global _gui_thread
    _gui_thread = QThread.currentThread() if thread is None else thread


def note_worker_started():
    """Called by `sys.Thread.start()`; arms the check.

    Until a worker exists there is nothing to catch, and `require_gui_thread`
    stays a single bool test.
    """
    global _workers_started
    _workers_started = True


def reset():
    """Forget both, for `LimekitApp.shutdown()` and between tests."""
    global _gui_thread, _workers_started
    _gui_thread = None
    _workers_started = False


def is_armed():
    return _workers_started and _gui_thread is not None


def require_gui_thread(what, owner):
    """Raise BridgeError if called from anywhere but the GUI thread.

    Raising rather than reporting is deliberate: inside a Lua callback this
    is caught by `guard()`, so the author gets a named, located error and the
    application keeps running -- which is strictly better than the crash the
    unchecked call would eventually produce.
    """
    # Globals read directly rather than via is_armed(): this runs on every
    # generated setter, and the disarmed path should cost one function call,
    # not two.
    if not _workers_started or _gui_thread is None:
        return
    current = QThread.currentThread()
    if current is _gui_thread:
        return
    name = current.objectName() or current.__class__.__name__
    raise BridgeError(
        f"{owner}.{what} was called from a worker thread ({name}); Qt widgets "
        f"may only be touched on the GUI thread. Use sys.Signal to hand the "
        f"update back: fire relay() from the thread and change widgets in its "
        f"setOnSignal handler."
    )
