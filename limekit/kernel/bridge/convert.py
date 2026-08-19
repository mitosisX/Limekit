"""Every Lua <-> Python crossing goes through here.

Previously each widget converted its own arguments, which is how ComboBox
and ListBox ended up disagreeing about whether a Python list was acceptable.
"""

import lupa

from limekit.kernel.errors import BridgeError

_runtime = None
_packer = None
_pairs_packer = None


def set_runtime(lua):
    """Called by LimeRuntime once the LuaRuntime exists."""
    global _runtime, _packer, _pairs_packer
    _runtime = lua
    _packer = None
    _pairs_packer = None


def _is_lua_table(value):
    return lupa.lua_type(value) == "table"


def _pack():
    """`function(...) return {...} end` -- builds a Lua table in one call.

    Deliberately not `LuaRuntime.table_from`. That call corrupts the Lua
    state when it runs *inside* a Lua callback, which is where nearly every
    conversion happens: a Qt signal calls a guarded Lua handler, the handler
    calls a framework method, and the method converts its result on the way
    back out.

    The damage does not show at the call site. It surfaces later as
    mis-bound calls -- a method invoked with arguments missing, an attribute
    lookup returning a different object's method, a class reported as "not
    callable". Measured on the `file-explorer` example, which rebuilds a
    listing from disk on every navigation: with `table_from` it failed on
    the 8th round trip.

    Every crossing of the boundary is exposure, so a table is built in a
    single call with the values as varargs rather than by creating an empty
    table and assigning into it element by element.
    """
    global _packer
    if _packer is None:
        _packer = _runtime.eval("function(...) return {...} end")
    return _packer


def _pack_pairs():
    """The same, for string-keyed tables: alternating key, value, ..."""
    global _pairs_packer
    if _pairs_packer is None:
        _pairs_packer = _runtime.eval("""
            function(...)
                local t, n = {}, select("#", ...)
                for i = 1, n, 2 do t[select(i, ...)] = select(i + 1, ...) end
                return t
            end
        """)
    return _pairs_packer


def to_lua(value):
    """Python -> Lua. Sequences become 1-indexed tables."""
    if _runtime is None:
        raise BridgeError("no Lua runtime is bound; call set_runtime() first")
    # Children are converted first, then the whole table is built in one
    # call. Doing it the obvious way -- create an empty table, then assign
    # into it -- costs one boundary crossing per element, and every crossing
    # is a chance to trip the fault described in `_pack`.
    if isinstance(value, dict):
        flat = []
        for key, item in value.items():
            flat.append(key)
            flat.append(to_lua(item))
        return _pack_pairs()(*flat)
    if isinstance(value, (list, tuple, set)):
        return _pack()(*[to_lua(item) for item in value])
    return value


def outbound(value):
    """Python -> Lua for a value leaving through a generated accessor.

    A Prop's setter runs `coerce` then `validate`; its getter used to run
    nothing at all, so a container-valued Prop handed Lua a raw Python list.
    `Splitter:setSizes({200, 500})` took a Lua table and `getSizes()` gave
    back something where `#` raised "attempt to get length of a POBJECT
    value" and `[1]` silently returned the *second* element -- 0-indexed,
    in a framework whose whole contract is 1-indexed.

    Only containers are converted. Everything else -- a QIcon, a layout, a
    string, a number -- passes through untouched, because those are either
    plain values Lua already understands or objects meant to be handed back
    to the framework rather than inspected.

    Unlike `to_lua`, a missing runtime is not an error here: widgets are
    constructed directly from Python in the test suite, with no Lua in
    sight, and a getter must keep working there.
    """
    if _runtime is None:
        return value
    if isinstance(value, (list, tuple, set, dict)):
        return to_lua(value)
    return value


def to_py(value):
    """Lua -> Python. A table with keys 1..n becomes a list, else a dict."""
    if not _is_lua_table(value):
        return value

    items = dict(value.items())
    keys = list(items)
    if keys and all(isinstance(k, int) for k in keys) and \
            sorted(keys) == list(range(1, len(keys) + 1)):
        return [to_py(items[k]) for k in sorted(keys)]
    return {k: to_py(v) for k, v in items.items()}


def as_sequence(value):
    """Accept a Lua table OR any Python sequence; always return a list.

    A string counts as a single item, not a sequence of characters.
    """
    if value is None:
        return []
    if _is_lua_table(value):
        result = to_py(value)
        return result if isinstance(result, list) else list(result.values())
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple, set)):
        return list(value)
    try:
        return list(value)
    except TypeError:
        return [value]


def as_mapping(value):
    if value is None:
        return {}
    if _is_lua_table(value):
        result = to_py(value)
        if isinstance(result, dict):
            return result
        return dict(enumerate(result, start=1))
    if isinstance(value, dict):
        return dict(value)
    raise BridgeError(f"expected a table or mapping, got {type(value).__name__}")


def as_callable(value):
    if not callable(value):
        raise BridgeError(f"expected a callable, got {type(value).__name__}")
    return value
