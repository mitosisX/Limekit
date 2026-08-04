import pytest
from PySide6.QtWidgets import QPushButton
from limekit.kernel.bridge.runtime import LimeRuntime
from limekit.kernel.registry import Registry
from limekit.kernel.declarative import LimeObject
from limekit.kernel.spec import Prop
from limekit.kernel.errors import LuaError


@pytest.fixture
def rt(qapp):
    class Button(LimeObject, QPushButton):
        text = Prop(str, default="Button", qt=("text", "setText"), coerce=str)

        def __init__(self, text="Button"):
            super().__init__()
            self.setText(text)

    reg = Registry()
    reg.register("ui.Button", Button)
    runtime = LimeRuntime(reg)
    runtime.install_modules()
    return runtime


def test_modules_are_requirable(rt):
    result = rt.eval(
        '(function() '
        'local ui = require("limekit.ui") '
        'return ui.Button("hi"):getText() '
        'end)()'
    )
    assert result == "hi"


def test_require_caches_module_table(rt):
    result = rt.eval(
        '(function() '
        'local a = require("limekit.ui") '
        'local b = require("limekit.ui") '
        'return a == b '
        'end)()'
    )
    assert result is True


def test_no_flat_globals_leak(rt):
    for name in ("Button", "eval", "str", "int", "dict", "tuple", "len"):
        assert rt.eval(f"{name} == nil"), f"{name} leaked into globals"


def test_lua_stdlib_print_survives(rt):
    # print is Lua's own stdlib function, not a Python shadow -- 2.0 only
    # removes the *Python* builtins 1.x used to inject, so print stays.
    assert rt.eval('type(print) == "function"')


def test_unknown_module_raises(rt):
    with pytest.raises(LuaError):
        rt.execute('require("limekit.nope")')


def test_syntax_error_reports_the_real_file(rt):
    with pytest.raises(LuaError) as exc:
        rt.execute("this is not lua", chunkname="scripts/main.lua")
    assert exc.value.source == "scripts/main.lua"


def test_syntax_error_reports_the_real_line(rt):
    # Two-line source with the syntax error on line 2: chunkname alone
    # cannot make this pass by coincidence, unlike a same-line echo would.
    source = "local x = 1\nthis is not lua\n"
    with pytest.raises(LuaError) as exc:
        rt.execute(source, chunkname="scripts/main.lua")
    assert exc.value.source == "scripts/main.lua"
    assert exc.value.line == 2


def test_runtime_error_reports_the_real_line(rt):
    source = "local x = 1\nerror('boom')\n"
    with pytest.raises(LuaError) as exc:
        rt.execute(source, chunkname="scripts/main.lua")
    assert exc.value.source == "scripts/main.lua"
    assert exc.value.line == 2
