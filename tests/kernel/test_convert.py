# tests/kernel/test_convert.py
import lupa
import pytest
from lupa import LuaRuntime
from limekit.kernel.bridge import convert
from limekit.kernel.errors import BridgeError


@pytest.fixture
def lua():
    runtime = LuaRuntime(unpack_returned_tuples=True)
    convert.set_runtime(runtime)
    yield runtime
    convert.set_runtime(None)


def test_as_sequence_accepts_a_lua_table(lua):
    table = lua.eval('{"a", "b", "c"}')
    assert convert.as_sequence(table) == ["a", "b", "c"]


def test_as_sequence_accepts_a_python_list(lua):
    """ListBox.setItems crashed on this; ComboBox.setItems did not."""
    assert convert.as_sequence(["a", "b"]) == ["a", "b"]


def test_as_sequence_accepts_a_tuple_and_generator(lua):
    assert convert.as_sequence(("a", "b")) == ["a", "b"]
    assert convert.as_sequence(i for i in range(3)) == [0, 1, 2]


def test_as_sequence_treats_a_string_as_one_item(lua):
    assert convert.as_sequence("abc") == ["abc"]


def test_as_sequence_of_none_is_empty(lua):
    assert convert.as_sequence(None) == []


def test_as_mapping_from_lua_table(lua):
    table = lua.eval('{x = 1, y = 2}')
    assert convert.as_mapping(table) == {"x": 1, "y": 2}


def test_to_py_detects_array_vs_map(lua):
    assert convert.to_py(lua.eval('{"a", "b"}')) == ["a", "b"]
    assert convert.to_py(lua.eval('{x = 1}')) == {"x": 1}


@pytest.mark.parametrize("source,expected", [
    # Contiguous 1..n keys -> list. This is the load-bearing branch of the
    # whole bridge: every widget accepting Lua tables depends on it telling
    # arrays from maps correctly.
    ('{[1]=1, [2]=2, [3]=3}', [1, 2, 3]),
    # A gap in the key sequence (1, 2, 4 -- no 3) must NOT be mistaken for
    # a contiguous array; it must become a dict keyed by the actual indices.
    ('{[1]=1, [2]=2, [4]=4}', {1: 1, 2: 2, 4: 4}),
])
def test_to_py_gap_in_keys_becomes_a_dict(lua, source, expected):
    assert convert.to_py(lua.eval(source)) == expected


def test_to_py_is_recursive(lua):
    assert convert.to_py(lua.eval('{a = {1, 2}}')) == {"a": [1, 2]}


def test_to_lua_round_trips(lua):
    assert convert.to_py(convert.to_lua(["a", "b"])) == ["a", "b"]
    assert convert.to_py(convert.to_lua({"x": 1})) == {"x": 1}


def test_to_lua_without_a_runtime_raises():
    convert.set_runtime(None)
    with pytest.raises(BridgeError, match="runtime"):
        convert.to_lua([1, 2])


def test_as_callable_accepts_a_lua_function(lua):
    fn = lua.eval('function(x) return x + 1 end')
    assert convert.as_callable(fn)(1) == 2


def test_as_callable_rejects_a_non_callable(lua):
    with pytest.raises(BridgeError, match="callable"):
        convert.as_callable(42)


# -- outbound (generated getters) --------------------------------------------

def test_outbound_converts_containers_to_lua_tables(lua):
    """A Prop getter used to hand Lua a raw Python list.

    `Splitter:setSizes({200, 500})` accepted a Lua table while `getSizes()`
    returned something where `#` raised "attempt to get length of a POBJECT
    value" and `[1]` silently gave the *second* element -- 0-indexed, in a
    framework whose contract is 1-indexed.
    """
    table = convert.outbound([10, 20, 30])
    assert lupa.lua_type(table) == "table"
    assert list(table.values()) == [10, 20, 30]
    assert table[1] == 10                    # 1-indexed, as Lua expects


@pytest.mark.parametrize("value", ["text", 42, 3.5, True, None])
def test_outbound_passes_plain_values_through(lua, value):
    assert convert.outbound(value) is value


def test_outbound_leaves_qt_objects_alone(lua):
    """Icons, layouts and the like are handed back to the framework, not read."""
    from PySide6.QtGui import QIcon
    icon = QIcon()
    assert convert.outbound(icon) is icon


def test_outbound_without_a_runtime_returns_the_value_unchanged():
    """Widgets are built straight from Python in this suite, with no Lua bound."""
    convert.set_runtime(None)
    payload = [1, 2, 3]
    assert convert.outbound(payload) is payload
