import pytest
from limekit.kernel.errors import (
    LimekitError, BridgeError, RegistryError, ProjectError,
    RouteError, LuaError, WidgetCallbackError,
)


@pytest.mark.parametrize("cls", [
    BridgeError, RegistryError, ProjectError, RouteError,
    LuaError, WidgetCallbackError,
])
def test_all_errors_share_a_root(cls):
    assert issubclass(cls, LimekitError)


def test_lua_error_carries_source_and_line():
    err = LuaError("bad syntax", source="scripts/main.lua", line=47)
    assert err.source == "scripts/main.lua"
    assert err.line == 47
    assert "scripts/main.lua:47" in str(err)


def test_lua_error_without_line_omits_it():
    err = LuaError("boom", source="scripts/main.lua")
    assert err.line is None
    assert "scripts/main.lua" in str(err)
    assert ":None" not in str(err)


def test_widget_callback_error_names_widget_and_event():
    err = WidgetCallbackError("handler failed", widget="Button", event="onClick")
    assert err.widget == "Button"
    assert err.event == "onClick"
    assert "Button.onClick" in str(err)


# -- splitting a raw lupa error apart ------------------------------------

RAW = (
    '[string "scripts/main.lua"]:55: this handler always fails\n'
    'stack traceback:\n'
    '\t[string "scripts/main.lua"]:55: in function <[string "scripts/main.lua"]:54>\n'
    "\t[C]: in global 'error'"
)


def test_parse_lua_error_separates_message_location_and_traceback():
    from limekit.kernel.errors import parse_lua_error

    message, source, line, trace = parse_lua_error(RAW)

    assert message == "this handler always fails"
    assert source == "scripts/main.lua"
    assert line == 55
    assert trace.startswith("stack traceback:")


def test_parse_lua_error_without_a_location():
    from limekit.kernel.errors import parse_lua_error

    message, source, line, trace = parse_lua_error("something went wrong")

    assert message == "something went wrong"
    assert line is None
    assert trace == ""


def test_widget_callback_error_reads_as_one_line():
    """The message names the widget, event, file and line -- and nothing else.

    It used to carry Lua's whole stack traceback, so a console printing the
    message printed five lines and buried the one that mattered.
    """
    from limekit.kernel.errors import WidgetCallbackError

    error = WidgetCallbackError.from_exception(
        Exception(RAW), widget="Button", event="onClick")

    assert str(error) == (
        "Button.onClick: scripts/main.lua:55: this handler always fails")
    assert "\n" not in str(error)
    assert error.source == "scripts/main.lua"
    assert error.line == 55
    assert error.details.startswith("stack traceback:")


def test_widget_callback_error_invents_no_location_for_a_python_failure():
    from limekit.kernel.errors import WidgetCallbackError

    error = WidgetCallbackError.from_exception(
        TypeError("not callable"), widget="ListBox", event="onItemSelect")

    assert str(error) == "ListBox.onItemSelect: not callable"
    assert error.source is None and error.line is None
