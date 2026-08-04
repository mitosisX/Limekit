# tests/kernel/test_convert.py
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
