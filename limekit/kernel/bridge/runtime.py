"""Owns the LuaRuntime and exposes the registry as requirable modules."""

import lupa
from lupa import LuaRuntime

from limekit.kernel.bridge import convert
from limekit.kernel.errors import LuaError, parse_lua_error

# Empirically, a fresh lupa.LuaRuntime() injects no Python builtins into Lua
# globals at all -- eval/str/int/dict/tuple/len were never present. 1.x's
# actual defect was that gather_additional_parts *explicitly injected*
# Python's builtins as Lua globals; simply not doing that is the real fix,
# and this list is belt-and-braces (nil-ing something already absent is a
# no-op). `print` is deliberately NOT here: it's Lua's own stdlib function,
# not a Python shadow, and removing it would take away a legitimate
# debugging facility for zero security benefit.
#
# This does NOT cover lupa's own `python` table (python.eval, python.builtins,
# python.as_attrgetter, ...). That table is installed by LuaRuntime itself,
# not by anything in this list, and register_eval/register_builtins are
# disabled below to close it. See LimeRuntime.__init__.
_DISALLOWED_GLOBALS = ("eval", "str", "int", "dict", "tuple", "len")


class LimeRuntime:
    """The Lua side of the bridge."""

    def __init__(self, registry, *, package="limekit"):
        self.registry = registry
        self.package = package
        # register_eval and register_builtins default to True in lupa and
        # install a `python` table with python.eval (arbitrary Python source
        # execution) and python.builtins (e.g. python.builtins.open) reachable
        # from any Lua script. Disabling both is the actual fix for C1; the
        # AST sandbox in toolkit/text.py is otherwise trivially bypassable.
        self.lua = LuaRuntime(unpack_returned_tuples=True,
                              register_eval=False, register_builtins=False)
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
        both runner.py and error_handler.py. The parsing itself lives in
        kernel/errors so that `guard` splits a failing handler's error the
        same way -- there were two copies of this and they disagreed about
        whether the stack traceback belonged in the message.
        """
        message, source, line, _ = parse_lua_error(str(exc),
                                                   fallback_source=chunkname)
        return LuaError(message, source=source, line=line)
