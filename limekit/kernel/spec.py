"""Inert specification objects.

These describe a widget's surface; they never intercept attribute access.
The collector in declarative.py reads them, generates accessors, then
removes them from the class (see constraint C1 in the spec).
"""


def _capitalise(name):
    return name[0].upper() + name[1:]


class _Spec:
    """Shared name-recording behaviour."""

    name = None

    def __set_name__(self, owner, name):
        self.name = name


class Prop(_Spec):
    """A readable/writable property backed by a pair of Qt methods."""

    def __init__(self, type_, *, default=None, qt=None, coerce=None,
                 validate=None, doc="", lua_name=None):
        if not qt or len(qt) != 2:
            raise ValueError(
                "Prop requires qt=(getter_name, setter_name); "
                "the kernel binds those functions at generation time."
            )
        self.type = type_
        self.default = default
        self.qt = tuple(qt)
        self.coerce = coerce
        self.validate = validate
        self.doc = doc
        self.lua_name = lua_name

    def accessor_names(self):
        """Return (getter, setter, alias).

        Booleans additionally get an `is<Name>` alias so Lua can read
        `button:isFlat()` as well as `button:getFlat()`.
        """
        base = _capitalise(self.lua_name or self.name)
        alias = f"is{base}" if self.type is bool else None
        return f"get{base}", f"set{base}", alias


class Event(_Spec):
    """A Qt signal exposed to Lua as a `setOn<Name>` handler slot."""

    def __init__(self, qt_signal, *, passes_self=True, args=(), doc=""):
        self.qt_signal = qt_signal
        self.passes_self = passes_self
        self.args = tuple(args)
        self.doc = doc

    def setter_name(self):
        return f"set{_capitalise(self.name)}"


class Method(_Spec):
    """A Qt method re-exported to Lua under a possibly different name."""

    def __init__(self, *, qt=None, doc="", lua_name=None):
        self.qt = qt
        self.doc = doc
        self.lua_name = lua_name
