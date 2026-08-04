"""Thread and Signal (`limekit.services.concurrency`).

1.x's `Thread.sleep(self): self.sleep()` recursed into itself
unconditionally -- there is no test for that shape here on purpose; a test
asserting "does not hang forever" would itself hang on a regression. The
replacement `sleep(seconds)` is exercised directly instead.
"""

import pytest

from limekit.kernel.bridge.guard import reset_error_sink, set_error_sink
from limekit.services.concurrency import Signal, Thread


@pytest.fixture(autouse=True)
def sink():
    captured = []
    set_error_sink(captured.append)
    yield captured
    reset_error_sink()


def test_thread_run_invokes_the_handler(qapp):
    thread = Thread()
    seen = []
    assert thread.setOnThreadRun(lambda self: seen.append(self)) is thread
    thread.run()                      # call directly; no real OS thread needed
    assert seen == [thread]


def test_thread_onthreadrun_is_guarded(qapp, sink):
    thread = Thread()
    thread.setOnThreadRun(lambda self: 1 / 0)
    thread.run()
    assert len(sink) == 1


def test_thread_sleep_does_not_recurse_forever(qapp):
    """Regression guard for the 1.x `def sleep(self): self.sleep()` bug:
    sleep(0) must return almost immediately, not blow the stack."""
    thread = Thread()
    assert thread.sleep(0) is thread


def test_thread_start_stop_and_is_running(qapp):
    thread = Thread()
    assert thread.isRunning() is False
    thread.setOnThreadRun(lambda self: None)
    thread.start()
    thread.wait(1000)
    assert thread.isRunning() is False


def test_signal_relay_invokes_the_handler(qapp):
    signal = Signal()
    seen = []
    assert signal.setOnSignal(lambda self: seen.append(self)) is signal
    assert signal.relay() is signal
    assert seen == [signal]


def test_signal_onsignal_is_guarded(qapp, sink):
    signal = Signal()
    signal.setOnSignal(lambda self: 1 / 0)
    signal.relay()
    assert len(sink) == 1
