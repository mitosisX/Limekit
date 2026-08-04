import pytest
from PySide6.QtWidgets import QPushButton
from limekit.kernel.bridge.guard import guard, set_error_sink, reset_error_sink
from limekit.kernel.declarative import LimeObject
from limekit.kernel.spec import Event
from limekit.kernel.errors import WidgetCallbackError


@pytest.fixture(autouse=True)
def sink():
    captured = []
    set_error_sink(captured.append)
    yield captured
    reset_error_sink()


def test_guard_contains_exceptions(sink):
    wrapped = guard(lambda: 1 / 0, widget="Button", event="onClick")
    wrapped()                                    # must not raise
    assert len(sink) == 1
    assert isinstance(sink[0], WidgetCallbackError)


def test_guard_names_the_widget_and_event(sink):
    wrapped = guard(lambda: 1 / 0, widget="ComboBox", event="onItemSelect")
    wrapped()
    assert sink[0].widget == "ComboBox"
    assert sink[0].event == "onItemSelect"


def test_guard_passes_through_return_values(sink):
    wrapped = guard(lambda x: x * 2, widget="W", event="e")
    assert wrapped(21) == 42
    assert sink == []


def test_event_handler_is_guarded_end_to_end(qapp, sink):
    class Button(LimeObject, QPushButton):
        onClick = Event("clicked", passes_self=True)

    b = Button()
    b.setOnClick(lambda widget: 1 / 0)
    b.click()                                    # must not raise
    assert len(sink) == 1


def test_handler_receives_the_widget_when_passes_self(qapp, sink):
    class Button(LimeObject, QPushButton):
        onClick = Event("clicked", passes_self=True)

    seen = []
    b = Button()
    b.setOnClick(seen.append)
    b.click()
    assert seen == [b]


def test_replacing_a_handler_disconnects_the_previous_one(qapp, sink):
    class Button(LimeObject, QPushButton):
        onClick = Event("clicked", passes_self=False)

    calls = []
    b = Button()
    b.setOnClick(lambda: calls.append("first"))
    b.setOnClick(lambda: calls.append("second"))
    b.click()
    assert calls == ["second"]
