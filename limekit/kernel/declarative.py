"""Spec collection and accessor generation.

Uses __init_subclass__ rather than a metaclass: type(QWidget) is a Shiboken
metaclass, and a naive `class Meta(type)` raises a metaclass conflict.
"""

from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import Prop, Event, Method

_SPEC_TYPES = (Prop, Event, Method)


def _resolve_qt_method(cls, name):
    """Find the native Qt method `name` in cls's MRO, skipping generated wrappers.

    A prop's setter/getter can be re-installed at every inheritance level
    (each subclass's __init_subclass__ calls _install_prop again for
    inherited props). If we just did getattr(cls, name), a child class
    would resolve straight to its *parent's* generated wrapper -- which
    happens to share the exact same name, e.g. `setText` -- rather than the
    real Qt method, stacking another layer of coerce/validate per
    generation. So we walk cls.__mro__ ourselves and skip any function
    tagged `_lime_generated` by a previous _install_prop call.

    Returns None if no untagged function exists anywhere in the MRO --
    meaning the class doesn't have the Qt method at all yet (an abstract
    mixin like `LimeWidget`, declared before it's combined with a concrete
    QWidget subclass).
    """
    for klass in cls.__mro__:
        fn = klass.__dict__.get(name)
        if fn is not None and not getattr(fn, "_lime_generated", False):
            return fn
    return None


def _install_prop(cls, prop):
    """Generate get/set accessors for one Prop.

    C2: the Qt functions are resolved HERE, before setattr runs. A Prop named
    `text` installs `setText`, which would otherwise shadow QPushButton.setText
    and recurse infinitely when the generated setter looked it up by name.

    The resolution itself is MRO-aware (see _resolve_qt_method) so that
    re-installing accessors for an inherited prop on a subclass finds the
    native Qt method rather than wrapping the parent's generated wrapper.
    If the Qt method doesn't exist anywhere in the MRO yet, this class is an
    abstract mixin -- skip installation; a concrete subclass that combines
    the mixin with a real Qt widget will install working accessors when
    it's created.
    """
    getter_name, setter_name, alias = prop.accessor_names()

    qt_get = _resolve_qt_method(cls, prop.qt[0])
    qt_set = _resolve_qt_method(cls, prop.qt[1])
    if qt_get is None or qt_set is None:
        return

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
    getter._lime_generated = True
    setter._lime_generated = True

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
