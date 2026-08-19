"""Catching widget access from a worker thread, and process-level lifetimes.

Two jobs, both about things the runtime must know of rather than any one
widget: which thread owns the widgets, and which objects have to outlive the
Lua chunk that created them.

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

# Every worker that has been created. A QThread built from Lua has no Qt
# parent, so QApplication.findChildren cannot see it -- and Qt aborts the
# whole process if a QThread is destroyed while it is still running. The
# registry lives here rather than in services/ so that kernel/app.py can wait
# for them at shutdown without importing upwards.
_workers = set()

# Timers, for the same reason: see register_timer.
_timers = set()

# Shown top-level windows. See register_window.
_windows = set()


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


def register_worker(thread):
    """Called by `sys.Thread.__init__`, so shutdown can wait for it."""
    _workers.add(thread)


def live_workers():
    """Every registered worker still running."""
    return tuple(t for t in _workers if t.isRunning())


def register_timer(timer):
    """Called by `sys.Timer.__init__`, so shutdown can stop it.

    A QTimer outlives the Lua runtime that owns its callback. Left running,
    it fires into a torn-down runtime and reports "Internal C++ object
    already deleted" -- the same shape of problem as a worker thread
    surviving shutdown.
    """
    _timers.add(timer)


def live_timers():
    """Every registered timer still ticking."""
    return tuple(t for t in _timers if t.isActive())


def register_window(window):
    """Called by `Window.show()`, to keep the window alive.

    A Lua script's top-level variables die with the chunk. `main.lua` ends
    with `window:show()` and then returns, so the only reference to the
    window is a local in a finished chunk -- and the next Lua collection
    frees it, taking the entire application with it. One
    `collectgarbage("collect")` was enough to leave a booted app with no
    top-level widgets at all.

    Nothing in the Lua is wrong; it reads exactly as the documentation says
    it should. So the framework holds the reference instead.
    """
    _windows.add(window)


def forget_window(window):
    """Called when a window closes, so a closed window can be collected."""
    _windows.discard(window)


def reset():
    """Forget all three, for `LimekitApp.shutdown()` and between tests."""
    global _gui_thread, _workers_started
    _gui_thread = None
    _workers_started = False
    _workers.clear()
    _timers.clear()
    _windows.clear()


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
