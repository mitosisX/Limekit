"""Owns the LuaRuntime and exposes the registry as requirable modules."""

import re

import lupa
from lupa import LuaRuntime

from limekit.kernel.bridge import convert
from limekit.kernel.errors import LuaError

# Lua reports errors as [string "name"]:LINE: message. Runtime errors start
# with that directly; compile/syntax errors are prefixed with
# "error loading code: " first, so this must SEARCH the text, not anchor to
# its start.
_LOCATION = re.compile(r'\[string "(?P<source>[^"]*)"\]:(?P<line>\d+):\s*(?P<msg>.*)',
                       re.DOTALL)

# Empirically, a fresh lupa.LuaRuntime() injects no Python builtins into Lua
# globals at all -- eval/str/int/dict/tuple/len were never present. 1.x's
# actual defect was that gather_additional_parts *explicitly injected*
# Python's builtins as Lua globals; simply not doing that is the real fix,
# and this list is mostly belt-and-braces (nil-ing something already absent
# is a no-op). `print` is deliberately NOT here: it's Lua's own stdlib
# function, not a Python shadow, and removing it would take away a
# legitimate debugging facility for zero security benefit.
_DISALLOWED_GLOBALS = ("eval", "str", "int", "dict", "tuple", "len")


class LimeRuntime:
    """The Lua side of the bridge."""

    def __init__(self, registry, *, package="limekit"):
        self.registry = registry
        self.package = package
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        convert.set_runtime(self.lua)
        self._strip_globals()

    def _strip_globals(self):
        g = self.lua.globals()
        for name in _DISALLOWED_GLOBALS:
            g[name] = None

    def globals(self):
        return self.lua.globals()

    def install_modules(self):
        """Expose every registered class through package.preload.

        Lua then reaches them with `require("limekit.ui")`, so nothing is
        installed as a bare global.

        A Python callable assigned straight into a Lua table stays
        `userdata` from Lua's point of view -- `require`'s preload searcher
        only accepts entries where `type(loader) == "function"`, so a raw
        Python lambda is silently skipped and require() falls through to
        the file-based searchers and fails. Wrapping the loader in a tiny
        Lua closure makes it a real Lua function.
        """
        preload = self.lua.eval("package.preload")
        wrap = self.lua.eval(
            "function(loader) return function(...) return loader(...) end end"
        )
        for module, members in self.registry.modules().items():
            table = self.lua.table_from(dict(members))
            preload[f"{self.package}.{module}"] = wrap(
                lambda *_args, _t=table: _t
            )

    def execute(self, source, chunkname="<limekit>"):
        return self._run(self.lua.execute, source, chunkname)

    def eval(self, source, chunkname="<limekit>"):
        return self._run(self.lua.eval, source, chunkname)

    def _run(self, fn, source, chunkname):
        try:
            return fn(source, name=chunkname)
        except lupa.LuaError as exc:
            raise self._translate(exc, chunkname) from exc

    @staticmethod
    def _translate(exc, chunkname):
        """Turn a raw lupa error into a LuaError carrying source and line.

        This replaces the rfind('>"]') string-surgery that used to live in
        both runner.py and error_handler.py.

        Lua's message body is followed by a "stack traceback:" section; we
        keep only the first line for LuaError's message (the source/line
        are already captured structurally in .source/.line), so callers
        printing the exception don't get a multi-line traceback dump.
        """
        text = str(exc)
        match = _LOCATION.search(text)
        if match:
            msg = match.group("msg").strip().splitlines()[0]
            return LuaError(
                msg,
                source=match.group("source") or chunkname,
                line=int(match.group("line")),
            )
        return LuaError(text.splitlines()[0], source=chunkname)
