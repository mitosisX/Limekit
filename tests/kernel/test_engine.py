"""The bridge runs on Lua 5.4, and nothing reaches past the pin.

See limekit/kernel/bridge/engine.py for why 5.5 is not used. A module that
did a bare `import lupa` would get 5.5 again -- and with it Lua tables its
`lua_type` cannot recognise -- so the pin is checked from both ends.
"""

import re
from pathlib import Path

import limekit


def test_the_engine_is_lua_54():
    from limekit.kernel.bridge.engine import lupa
    assert lupa.__name__ == "lupa.lua54"


def test_the_runtime_is_built_on_the_pinned_engine():
    from limekit.kernel.bridge import runtime
    from limekit.kernel.bridge.engine import LuaRuntime
    assert runtime.LuaRuntime is LuaRuntime


def test_the_runtime_reports_lua_54():
    from limekit.kernel.bridge.engine import LuaRuntime
    lua = LuaRuntime()
    assert lua.eval("_VERSION") == "Lua 5.4"


# 1.x code that the 2.0 engine never imports; it keeps its own lupa use.
_LEGACY = ("components", "engine", "core", "gui", "utils", "runner.py")


def test_no_2x_module_imports_lupa_directly():
    root = Path(limekit.__file__).parent
    bare = re.compile(r"^\s*(import lupa\b(?!\.)|from lupa\b(?!\.lua54) import)", re.M)
    offenders = []
    for path in root.rglob("*.py"):
        relative = path.relative_to(root).as_posix()
        if relative.startswith(_LEGACY) or relative == "kernel/bridge/engine.py":
            continue
        if bare.search(path.read_text(encoding="utf-8", errors="replace")):
            offenders.append(relative)
    assert offenders == []
