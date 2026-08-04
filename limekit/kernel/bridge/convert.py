"""Every Lua <-> Python crossing goes through here.

Previously each widget converted its own arguments, which is how ComboBox
and ListBox ended up disagreeing about whether a Python list was acceptable.
"""

import lupa

from limekit.kernel.errors import BridgeError

_runtime = None


def set_runtime(lua):
    """Called by LimeRuntime once the LuaRuntime exists."""
    global _runtime
    _runtime = lua


def _is_lua_table(value):
    return lupa.lua_type(value) == "table"


def to_lua(value):
    """Python -> Lua. Sequences become 1-indexed tables."""
    if _runtime is None:
        raise BridgeError("no Lua runtime is bound; call set_runtime() first")
    if isinstance(value, dict):
        return _runtime.table_from({k: to_lua(v) for k, v in value.items()})
    if isinstance(value, (list, tuple, set)):
        return _runtime.table_from([to_lua(v) for v in value])
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
