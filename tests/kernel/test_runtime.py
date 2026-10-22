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
        text = Prop(str, qt=("text", "setText"), coerce=str)

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


def test_python_eval_and_builtins_are_disabled(rt):
    """C1: register_eval/register_builtins must be off, or python.eval and
    python.builtins reach arbitrary Python execution and filesystem access
    from any Lua script, bypassing the toolkit/text.py AST sandbox entirely."""
    assert rt.eval("python == nil or python.eval == nil"), \
        "python.eval is reachable -- arbitrary Python execution from Lua"
    assert rt.eval("python == nil or python.builtins == nil"), \
        "python.builtins is reachable -- e.g. python.builtins.open(...)"


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


# -- colon syntax on Qt natives ------------------------------------------------
#
# lupa drops the duplicated self from `obj:m()` only for Python-defined bound
# methods; a Qt native is a builtin method, so `b:toolTip()` reached Qt as
# `toolTip(b)` and raised "takes no arguments (1 given)". The runtime's
# attribute getter now extends lupa's own rule to builtin methods.

def test_colon_call_on_a_raw_qt_object_works(rt):
    from PySide6.QtWidgets import QTableWidgetItem

    button = QPushButton("hi")
    button.setToolTip("tip")
    item = QTableWidgetItem("cell")
    call = rt.eval("function(b, i) return b:toolTip(), i:text(), b:text() end")
    assert call(button, item) == ("tip", "cell", "hi")


def test_colon_call_passes_the_remaining_arguments(rt):
    button = QPushButton()
    rt.eval("function(b) b:setToolTip('set by colon') end")(button)
    assert button.toolTip() == "set by colon"


def test_dot_call_on_a_qt_native_still_works(rt):
    button = QPushButton()
    rt.eval("function(b) b.setToolTip('set by dot') end")(button)
    assert button.toolTip() == "set by dot"
    assert rt.eval("function(b) return b.toolTip() end")(button) == "set by dot"


def test_dot_call_passing_the_object_to_itself_is_not_mangled(rt):
    """`w.isAncestorOf(w)` legitimately passes w as an argument.

    The first argument is the object the method is bound to, so it looks
    exactly like a colon call. Dropping it leaves a call Qt refuses before
    running anything, and the original arguments are then used as given.
    """
    from PySide6.QtWidgets import QWidget

    w = QWidget()
    assert rt.eval("function(w) return w.isAncestorOf(w) end")(w) is True
    assert rt.eval("function(w) return w:isAncestorOf(w) end")(w) is True


def test_python_methods_and_indexing_are_untouched(rt):
    class Thing:
        def __init__(self):
            self.value = 4

        def twice(self, n):
            return n * 2

    thing = Thing()
    assert rt.eval("function(t) return t:twice(3), t.twice(5), t.value end")(thing) \
        == (6, 10, 4)
    # Objects with __getitem__ keep lupa's default: item access, 0-based.
    assert rt.eval("function(l) return l[1] end")([5, 6]) == 6
    assert rt.eval("function(d) return d.x, d['y'] end")({"x": 1, "y": 2}) == (1, 2)


def test_missing_attribute_still_raises(rt):
    rt.globals().probe = QPushButton()
    # lupa re-raises the Python exception itself, as it did before the getter.
    with pytest.raises(AttributeError, match="noSuchThing"):
        rt.execute("probe.noSuchThing()")
