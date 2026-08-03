"""Spec collection and accessor generation.

Uses __init_subclass__ rather than a metaclass: type(QWidget) is a Shiboken
metaclass, and a naive `class Meta(type)` raises a metaclass conflict.
"""

from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import Prop, Event, Method

_SPEC_TYPES = (Prop, Event, Method)


def _install_prop(cls, prop):
    """Generate get/set accessors for one Prop.

    C2: the Qt functions are resolved HERE, before setattr runs. A Prop named
    `text` installs `setText`, which would otherwise shadow QPushButton.setText
    and recurse infinitely when the generated setter looked it up by name.
    """
    getter_name, setter_name, alias = prop.accessor_names()

    qt_get = getattr(cls, prop.qt[0])
    qt_set = getattr(cls, prop.qt[1])
    coerce, validate, label = prop.coerce, prop.validate, prop.name

    def getter(self, _g=qt_get):
        return _g(self)

    def setter(self, value, _s=qt_set, _c=coerce, _v=validate, _n=label):
        if _c is not None:
            value = _c(value)
        if _v is not None and not _v(value):
            raise BridgeError(f"invalid value for {_n!r}: {value!r}")
        _s(self, value)
        return self          # allow chaining from Lua

    getter.__name__ = getter_name
    setter.__name__ = setter_name
    getter.__doc__ = setter.__doc__ = prop.doc or None

    setattr(cls, getter_name, getter)
    setattr(cls, setter_name, setter)
    if alias:
        setattr(cls, alias, getter)


class LimeObject:
    """Base for every class exposed to Lua.

    Collects Prop/Event/Method declarations across the MRO, then deletes the
    spec objects from the class so the Qt attributes they describe are no
    longer shadowed (constraint C1).
    """

    __lime__ = None
    __props__ = ()
    __events__ = ()
    __methods__ = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        props, events, methods = {}, {}, {}

        # Reversed MRO so a subclass declaration overwrites its parent's.
        #
        # A parent's own Prop/Event/Method objects are gone from its
        # __dict__ by the time we get here -- they were delattr'd when the
        # parent itself was built (C1). So each ancestor contributes twice:
        # its already-collected __props__/__events__/__methods__ tuples
        # (inherited specs), then a scan of its still-live __dict__ (specs
        # declared directly on it, only non-empty for `cls` itself since
        # earlier ancestors were already cleaned).
        for base in reversed(cls.__mro__):
            own = vars(base)
            for p in own.get("__props__", ()):
                props[p.name] = p
            for e in own.get("__events__", ()):
                events[e.name] = e
            for m in own.get("__methods__", ()):
                methods[m.name] = m
            for key, value in own.items():
                if isinstance(value, Prop):
                    props[key] = value
                elif isinstance(value, Event):
                    events[key] = value
                elif isinstance(value, Method):
                    methods[key] = value

        # C1: drop the spec objects declared on THIS class. Parents were
        # already cleaned when they were themselves created.
        for key, value in list(vars(cls).items()):
            if isinstance(value, _SPEC_TYPES):
                delattr(cls, key)

        cls.__props__ = tuple(props.values())
        cls.__events__ = tuple(events.values())
        cls.__methods__ = tuple(methods.values())

        for prop in cls.__props__:
            _install_prop(cls, prop)
