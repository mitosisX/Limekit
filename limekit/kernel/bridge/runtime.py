"""Owns the LuaRuntime and exposes the registry as requirable modules."""

import types

from limekit.kernel.bridge import convert
from limekit.kernel.bridge.engine import LuaRuntime, lupa
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
# disabled below. See LimeRuntime.__init__.
#
# None of this is a sandbox, and nothing here should be read as one. Any
# Python object Lua can reach leads back to Python's builtins (through
# `obj.__class__.__init__.__globals__`), and Lua's own `io` and `os` are
# present. That is the right trade for what Limekit runs: an app's own code,
# with the user's permissions, like any desktop program. Running Lua someone
# else wrote -- plugins, shared templates -- would need a real boundary first:
# refusing dunder attributes in `_get_attribute`, and removing io/os/load.
_DISALLOWED_GLOBALS = ("eval", "str", "int", "dict", "tuple", "len")


def _colon_safe(method, owner):
    """A Qt-native bound method that tolerates Lua's colon syntax.

    `obj:m(a)` reaches Python as `obj.m(obj, a)`. lupa already drops that
    duplicated self for Python-defined bound methods, but its check is
    `PyMethod_Check`, which a Qt native -- a builtin method -- fails. So
    `button:toolTip()` raised "takes no arguments (1 given)" while
    `button:getText()` worked, and every raw Qt object handed to Lua (a
    QTableWidgetItem, an event) was a trap.

    This applies lupa's own rule to builtin methods, with one guard lupa
    does not have. A dot call can legitimately pass the object to itself --
    `w.isAncestorOf(w)` -- which looks exactly like a colon call. So the
    call is tried without the duplicate first; if Qt refuses the arguments,
    it is retried exactly as written. A refusal is recognised as a
    TypeError raised by the native call itself (no Python frame beneath
    this one): Qt's overload resolution rejects arguments before running
    anything, so the first attempt had no effect. A TypeError from Python
    code the native called into carries that code's frames and is re-raised
    untouched, never retried.

    Calls whose first argument is not the owner are passed through as is.
    """

    def call(*args, **kwargs):
        if not args or args[0] is not owner:
            return method(*args, **kwargs)
        try:
            return method(*args[1:], **kwargs)
        except TypeError as exc:
            if exc.__traceback__.tb_next is not None:
                raise
            first = exc
        try:
            return method(*args, **kwargs)
        except TypeError:
            # Both readings were refused; the colon reading is the
            # framework's convention, so its message is the one to show.
            raise first from None

    call.__name__ = getattr(method, "__name__", "method")
    call.__doc__ = getattr(method, "__doc__", None)
    return call


def _get_attribute(obj, name):
    """lupa's attribute getter: its default lookup, plus `_colon_safe`.

    Installing a getter replaces lupa's own dispatch entirely, so this
    reproduces it: an object with `__getitem__` is indexed by item (which
    is how a Python list answers `l[1]`), anything else by attribute. That
    is the rule lupa applies when it wraps an object. The one difference:
    `python.as_attrgetter`/`as_itemgetter` wrappers no longer override it,
    since lupa hands the getter the unwrapped object. Nothing in the 2.0
    framework uses them.

    Only builtin methods bound to `obj` are wrapped; Python-defined methods
    already work with colon syntax and are returned unchanged. The wrapper
    is a plain function, so passing a Qt-native method as a *value* (e.g.
    to `connect`) hands over a callable rather than the bound slot itself.
    """
    if hasattr(obj, "__getitem__"):
        return obj[name]
    if isinstance(name, bytes):
        name = name.decode("utf-8")
    value = getattr(obj, name)
    if isinstance(value, types.BuiltinMethodType) and \
            getattr(value, "__self__", None) is obj:
        return _colon_safe(value, obj)
    return value


class LimeRuntime:
    """The Lua side of the bridge."""

    def __init__(self, registry, *, package="limekit"):
        self.registry = registry
        self.package = package
        # register_eval and register_builtins default to True in lupa and
        # install a `python` table with python.eval (arbitrary Python source
        # execution) and python.builtins (e.g. python.builtins.open) reachable
        # from any Lua script. Disabling both removes those two direct doors,
        # and keeps sys.Expr's arithmetic-only evaluator (toolkit/text.py)
        # from being the easy way round. It does not make Lua untrusted-safe:
        # see the note above _DISALLOWED_GLOBALS.
        # The getter makes Qt-native methods callable with colon syntax;
        # see _get_attribute. No setter: lupa's default assignment stands.
        self.lua = LuaRuntime(unpack_returned_tuples=True,
                              register_eval=False, register_builtins=False,
                              attribute_handlers=(_get_attribute, None))
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
