"""Converting Python values to Lua from inside a Lua callback.

Almost every conversion happens in that position: a Qt signal calls a
guarded Lua handler, the handler calls a framework method, and the method
converts its result on the way back out. `LuaRuntime.table_from` corrupts
the Lua state when used there, and the damage does not appear at the call
site -- it surfaces later as mis-bound calls, which is close to impossible
to trace back from the error message.

The `file-explorer` example, which rebuilds a listing from disk on every
navigation, failed on the 8th round trip with `table_from` and survives
3000 without it.
"""

import pytest

from limekit.kernel.bridge import convert


@pytest.fixture
def lua():
    from lupa import LuaRuntime
    runtime = LuaRuntime(unpack_returned_tuples=True)
    convert.set_runtime(runtime)
    yield runtime
    convert.set_runtime(None)


def test_converts_lists_dicts_and_nesting(lua):
    assert list(convert.to_lua([1, 2, 3]).values()) == [1, 2, 3]

    mapping = convert.to_lua({"a": 1, "b": "two"})
    assert mapping.a == 1 and mapping.b == "two"

    nested = convert.to_lua([{"name": "x", "deep": [1, 2]}])
    assert nested[1].name == "x"
    assert list(nested[1].deep.values()) == [1, 2]


def test_lists_are_one_indexed(lua):
    table = convert.to_lua(["first", "second"])
    assert table[1] == "first"
    assert table[2] == "second"
    assert lua.eval("function(t) return #t end")(table) == 2


def test_repeated_conversion_from_inside_a_callback_stays_sane(lua):
    """The regression this module exists for.

    Python calls a Lua handler, which calls back into Python, which converts
    a nested structure -- the exact shape `fs.FileSystem.walkDir` produces --
    and does it hundreds of times. With `table_from` the state degrades and
    later calls start losing arguments or resolving to the wrong function.
    """
    rows = [{"name": f"n{i}", "path": f"/p/{i}", "is_dir": i % 2 == 0} for i in range(6)]

    problems = []

    def produce():
        return convert.to_lua(rows)

    def note(message):
        problems.append(message)

    lua.globals().produce = produce
    lua.globals().note = note

    handler = lua.eval("""
        function()
            local t = produce()
            if #t ~= 6 then note("length " .. tostring(#t)) return end
            for i = 1, 6 do
                local row = t[i]
                if type(row) ~= "table" then note("row " .. i .. " is " .. type(row)) return end
                if type(row.name) ~= "string" then note("row " .. i .. " name is " .. type(row.name)) return end
                if type(row.is_dir) ~= "boolean" then note("row " .. i .. " is_dir is " .. type(row.is_dir)) return end
            end
        end
    """)

    # Driven from Python, the way a Qt signal drives a handler.
    for _ in range(500):
        handler()

    assert problems == [], problems[:3]


def test_conversion_does_not_use_table_from():
    """A guard on the fix rather than on its effect.

    `table_from` is the call that breaks, and the failure it causes is
    remote and confusing, so catch a reach for it here instead. lupa's
    LuaRuntime is an immutable extension type and cannot be monkey-patched,
    so this reads the source.
    """
    import inspect

    source = inspect.getsource(convert.to_lua)
    assert "table_from" not in source, (
        "to_lua uses LuaRuntime.table_from; it corrupts the Lua state when "
        "called from inside a Lua callback -- see this module's docstring"
    )
