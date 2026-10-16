"""The Lua the bridge runs on: Lua 5.4, pinned.

lupa ships one module per Lua version, and a bare `import lupa` gives the
newest one -- Lua 5.5 from lupa 2.8 on. Under 5.5, a Lua handler re-entered
from a Qt signal while Lua is in the middle of a Python call leaves lupa's
object bookkeeping corrupt, and later attribute lookups hand back the wrong
Python object. Limer's designer hit it every time it opened: a TableItem's
setBackgroundColour fires cellChanged, the guarded handler runs, and a few
calls later `FileSystem.joinPaths` resolved to that TableItem's bound
setBackgroundColour. The same session on 5.4 is clean, run after run.

This is the failure tests/kernel/test_convert_reentrancy.py describes for
`table_from` -- mis-bound calls far from their cause -- reached by another
road. Pinning the engine closes the road rather than the one call site.

Everything that touches lupa imports it from here, so the engine is chosen
in one place. Lua tables made by one engine are not recognised by another's
`lua_type`, which is why a stray `import lupa` elsewhere would break
conversion outright rather than quietly.
"""

import lupa.lua54 as lupa

LuaRuntime = lupa.LuaRuntime
LuaError = lupa.LuaError
lua_type = lupa.lua_type
