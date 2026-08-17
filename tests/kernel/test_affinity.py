"""The GUI-thread check on generated setters (`limekit.kernel.affinity`).

Qt widgets may only be touched on the thread that created them. `sys.Thread`
makes breaking that rule easy and, before this check, silent -- the failure
was a crash or corruption at some unrelated later point, with nothing
pointing back at the cause.
"""

import pytest
from PySide6.QtCore import QThread

from limekit.kernel import affinity
from limekit.kernel.bridge.guard import reset_error_sink, set_error_sink
from limekit.kernel.errors import BridgeError


@pytest.fixture(autouse=True)
def clean_affinity():
    affinity.reset()
    yield
    affinity.reset()


@pytest.fixture(autouse=True)
def sink():
    captured = []
    set_error_sink(captured.append)
    yield captured
    reset_error_sink()


def _label(text="hi"):
    from limekit.widgets.label import Label
    return Label(text)


# -- disarmed by default ------------------------------------------------------

def test_check_is_inert_until_a_worker_starts(qapp):
    """An app that never uses sys.Thread must never pay for this."""
    affinity.set_gui_thread()
    assert affinity.is_armed() is False

    label = _label()
    label.setText("still fine")          # would be on the GUI thread anyway
    assert label.getText() == "still fine"


def test_check_is_inert_without_a_recorded_gui_thread(qapp):
    """Widgets built straight from Python, with no LimekitApp, keep working."""
    affinity.note_worker_started()
    assert affinity.is_armed() is False
    _label().setText("fine")


# -- armed --------------------------------------------------------------------

def test_gui_thread_setter_is_still_allowed(qapp):
    affinity.set_gui_thread()
    affinity.note_worker_started()
    assert affinity.is_armed() is True

    label = _label()
    label.setText("from the gui thread")
    assert label.getText() == "from the gui thread"


def test_setter_from_a_worker_thread_is_refused(qapp):
    """The real shape of the bug: a widget updated inside a thread handler."""
    affinity.set_gui_thread()

    label = _label()
    failures = []

    class Worker(QThread):
        def run(self):
            try:
                label.setText("from the worker")
            except BridgeError as exc:
                failures.append(str(exc))

    affinity.note_worker_started()
    worker = Worker()
    worker.start()
    assert worker.wait(5000), "worker thread did not finish"

    assert len(failures) == 1
    message = failures[0]
    assert "worker thread" in message
    assert "Label.text" in message or "text" in message
    assert "sys.Signal" in message           # tells the author what to do
    assert label.getText() == "hi"           # and the write did not happen


def test_worker_thread_error_is_reported_not_fatal(qapp, sink):
    """Inside a guarded Lua callback the refusal is reported, not raised.

    This is what makes the check safe to add: an app that was silently
    corrupting itself now prints a located error and keeps running.
    """
    from limekit.services.concurrency import Thread

    affinity.set_gui_thread()
    label = _label()

    thread = Thread()
    thread.setOnThreadRun(lambda _self: label.setText("from the worker"))
    thread.start()                        # arms the check, runs the handler
    assert thread.wait(5000)

    assert len(sink) == 1
    assert sink[0].widget == "Thread"
    assert sink[0].event == "onThreadRun"
    assert "worker thread" in str(sink[0])
    assert label.getText() == "hi"


def test_signal_is_the_documented_way_across(qapp):
    """sys.Signal hands the update back to the GUI thread, so it is allowed."""
    from limekit.services.concurrency import Signal, Thread

    affinity.set_gui_thread()
    label = _label()

    relay = Signal()
    relay.setOnSignal(lambda _self: label.setText("done"))

    thread = Thread()
    thread.setOnThreadRun(lambda _self: relay.relay())
    thread.start()
    assert thread.wait(5000)

    # The handler is invoked through the signal on the GUI thread; pump the
    # event loop so the queued connection is delivered.
    qapp.processEvents()
    assert label.getText() == "done"
