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
