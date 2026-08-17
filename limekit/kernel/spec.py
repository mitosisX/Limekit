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

    def __init__(self, type_, *, qt=None, coerce=None,
                 validate=None, doc="", lua_name=None):
        if not qt or len(qt) != 2:
            raise ValueError(
                "Prop requires qt=(getter_name, setter_name); "
                "the kernel binds those functions at generation time."
            )
        self.type = type_
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

    def __init__(self, qt_signal, *, passes_self=True, doc="", params=None):
        self.qt_signal = qt_signal
        self.passes_self = passes_self
        self.doc = doc
        # What the Qt signal delivers *after* the widget, as
        # ((name, lua_type), ...). The generated attach() passes the signal's
        # arguments straight through, so without this the stubs described
        # every handler as fun(widget) -- silently wrong for the ~20 events
        # that carry a value, an index or an item.
        self.params = tuple(params or ())

    def setter_name(self):
        return f"set{_capitalise(self.name)}"

    def handler_signature(self, owner):
        """The Lua type of the handler, e.g. `fun(widget: Table, row: integer)`."""
        parts = [f"widget: {owner}"] if self.passes_self else []
        parts.extend(f"{name}: {typename}" for name, typename in self.params)
        return f"fun({', '.join(parts)})"


class Method:
    """Type information for a hand-written method, attached by `@method`.

    Prop and Event describe things the kernel *generates*. A Method describes
    something that already exists -- `addChild`, `setData`, `addSeries` -- so
    the generators can see it.

    It is deliberately not a `_Spec`: declaring `addChild = Method(...)` in a
    class body would shadow the very method it documents, which is the C1
    problem all over again. It rides on the function instead, via the
    decorator below, and nothing in the class body changes.

    Attaching one is optional. `kernel.introspect.public_methods` finds
    hand-written methods whether or not they carry a Method, using the real
    signature; a Method only adds what introspection cannot recover -- Lua
    parameter types, the return type, and a written description.
    """

    def __init__(self, params=None, *, returns=None, doc=""):
        # {parameter name -> Lua type string}, e.g. {"row": "integer"}.
        self.params = dict(params or {})
        self.returns = returns
        self.doc = doc


def method(params=None, *, returns=None, doc=""):
    """Decorator attaching a `Method` to a hand-written method.

        @method({"x": "number", "y": "number"}, returns="self",
                doc="Adds a single point.")
        def append(self, x, y):
            ...

    `returns="self"` documents the chaining convention -- the generator turns
    it into the owning class's name.
    """

    def decorate(fn):
        target = fn.__func__ if isinstance(fn, (staticmethod, classmethod)) else fn
        target._lime_method = Method(params, returns=returns, doc=doc or target.__doc__ or "")
        return fn

    return decorate
