"""Spec collection and accessor generation.

Uses __init_subclass__ rather than a metaclass: type(QWidget) is a Shiboken
metaclass, and a naive `class Meta(type)` raises a metaclass conflict.
"""

from limekit.kernel import affinity
from limekit.kernel.bridge import convert
from limekit.kernel.bridge.guard import guard
from limekit.kernel.errors import BridgeError, RegistryError
from limekit.kernel.registry import registry
from limekit.kernel.spec import Prop, Event

# `Method` was removed from the public spec surface: it was collected into
# __methods__ but installed by nothing (all three generators ignored it).
# Reintroduce it in P1 with a real consumer rather than leaving it declared
# and dead -- see spec 1.1's own complaint about exactly this pattern.
_SPEC_TYPES = (Prop, Event)


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


def _safe_setattr(cls, name, value, *, prop_name, allow=()):
    """setattr, but refuse to silently clobber a name we did not generate.

    Two verified shapes this catches: a Prop whose generated accessor name
    collides with an unrelated Qt method (`fixedSize = Prop(..., qt=("size",
    "resize"))` would otherwise replace LimeWidget.setFixedSize), and a
    hand-written method silently replaced by a generated accessor of the
    same name (ComboBox.getText, if a future `text` Prop ever lands on
    ComboBox). Both used to fail silently at class-definition time; this
    turns them into an immediate, loud RegistryError instead.

    The whole MRO is checked (not just vars(cls)), the same way
    _resolve_qt_method looks past generated wrappers: a Qt method like
    setFixedSize lives on QWidget, several classes up from the widget that
    declares the colliding Prop, so a vars(cls)-only check would miss it.

    `allow` carries the exact qt_get/qt_set function objects _install_prop
    already resolved for THIS prop (see C2): the common case is a generated
    name that is deliberately identical to the underlying Qt method it
    wraps (a `text` Prop generates `setText`, shadowing QWidget.setText on
    purpose), and that intended shadow must not trip this check. A
    subclass re-installing an inherited prop is likewise fine -- the
    parent's accessor of the same name is tagged _lime_generated.
    """
    for klass in cls.__mro__:
        existing = klass.__dict__.get(name)
        if existing is not None:
            if not any(existing is a for a in allow) and \
                    not getattr(existing, "_lime_generated", False):
                raise RegistryError(
                    f"{cls.__name__}.{name} already exists on "
                    f"{klass.__name__} and is not a generated accessor; "
                    f"the {prop_name!r} spec cannot install its accessor "
                    f"there without silently replacing it"
                )
            break
    setattr(cls, name, value)


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

    # These close over qt_get/qt_set/coerce/... rather than binding them as
    # default arguments. The default-argument form is a common micro-optimisation,
    # but it puts the framework's internals in the *public* signature: a Lua
    # caller passing one argument too many silently overwrote the Qt method with
    # their own value. `label:setTextAlignment("hcenter", "bottom")` replaced
    # setAlignment with the string "bottom" and failed as "'str' object is not
    # callable", naming nothing useful. Now an extra argument is a plain,
    # honest TypeError about argument count.
    def getter(self):
        return convert.outbound(qt_get(self))

    def setter(self, value):
        # Mutating a widget off the GUI thread is undefined behaviour in Qt.
        # This is a bool test until a sys.Thread has actually been started.
        affinity.require_gui_thread(label, type(self).__name__)
        if coerce is not None:
            value = coerce(value)
        if validate is not None and not validate(value):
            raise BridgeError(f"invalid value for {label!r}: {value!r}")
        qt_set(self, value)
        return self          # allow chaining from Lua

    getter.__name__ = getter_name
    setter.__name__ = setter_name
    getter.__doc__ = setter.__doc__ = prop.doc or None
    getter._lime_generated = True
    setter._lime_generated = True

    _safe_setattr(cls, getter_name, getter, prop_name=prop.name, allow=(qt_get,))
    _safe_setattr(cls, setter_name, setter, prop_name=prop.name, allow=(qt_set,))
    if alias:
        _safe_setattr(cls, alias, getter, prop_name=prop.name, allow=(qt_get, qt_set))


def _install_event(cls, event):
    """Generate `setOn<Name>` for one Event.

    The generated setter is the only way to attach a handler, so every
    handler is guarded by construction.

    Unlike props, the Qt signal is resolved on the *instance* at attach
    time (`getattr(self, _sig)`), not on the class at generation time. A
    signal name like `clicked` is never shadowed by a generated name like
    `setOnClick`, so there's no C2 collision -- and because nothing here
    touches the class's MRO for the signal itself, installing this on an
    abstract mixin (before it's combined with a concrete Qt widget) is
    safe; no abstract-mixin deferral is needed.
    """
    setter_name = event.setter_name()
    signal_name, passes_self, label = event.qt_signal, event.passes_self, event.name
    slot_attr = f"_lime_slot_{event.name}"
    index_positions = event.index_positions()

    def attach(self, handler):
        # Closures, not default arguments -- see the note in _install_prop.
        _sig, _self, _ev = signal_name, passes_self, label
        _slot, _idx = slot_attr, index_positions
        signal = getattr(self, _sig)

        previous = getattr(self, _slot, None)
        if previous is not None:
            signal.disconnect(previous)

        widget_name = type(self).__name__

        def shift(args):
            """Qt counts positions from 0; every Lua-facing index counts from 1.

            A signal reporting "no selection" as -1 lands on 0, which is
            exactly what "nothing" means in 1-based counting -- and 0 is
            already rejected everywhere else as an out-of-range index.
            """
            if not _idx:
                return args
            shifted = list(args)
            for offset in _idx:
                value = shifted[offset] if offset < len(shifted) else None
                if isinstance(value, int) and not isinstance(value, bool):
                    shifted[offset] = value + 1
            return tuple(shifted)

        if _self:
            def call(*args, _h=handler, _w=self):
                return _h(_w, *shift(args))
        else:
            def call(*args, _h=handler):
                return _h(*shift(args))

        slot = guard(call, widget=widget_name, event=_ev)
        setattr(self, _slot, slot)
        signal.connect(slot)
        return self

    attach.__name__ = setter_name
    attach.__doc__ = event.doc or None
    attach._lime_generated = True
    _safe_setattr(cls, setter_name, attach, prop_name=event.name)


class LimeObject:
    """Base for every class exposed to Lua.

    Collects Prop/Event declarations across the MRO, then deletes the spec
    objects from the class so the Qt attributes they describe are no longer
    shadowed (constraint C1).
    """

    __lime__ = None
    __props__ = ()
    __events__ = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        props, events = {}, {}

        # Reversed MRO so a subclass declaration overwrites its parent's.
        #
        # A parent's own Prop/Event objects are gone from its __dict__ by
        # the time we get here -- they were delattr'd when the parent
        # itself was built (C1). So each ancestor contributes twice: its
        # already-collected __props__/__events__ tuples (inherited specs),
        # then a scan of its still-live __dict__ (specs declared directly
        # on it, only non-empty for `cls` itself since earlier ancestors
        # were already cleaned).
        for base in reversed(cls.__mro__):
            own = vars(base)
            for p in own.get("__props__", ()):
                props[p.name] = p
            for e in own.get("__events__", ()):
                events[e.name] = e
            for key, value in own.items():
                if isinstance(value, Prop):
                    props[key] = value
                elif isinstance(value, Event):
                    events[key] = value

        # C1: drop the spec objects declared on THIS class. Parents were
        # already cleaned when they were themselves created.
        for key, value in list(vars(cls).items()):
            if isinstance(value, _SPEC_TYPES):
                delattr(cls, key)

        cls.__props__ = tuple(props.values())
        cls.__events__ = tuple(events.values())

        for prop in cls.__props__:
            _install_prop(cls, prop)

        for event in cls.__events__:
            _install_event(cls, event)

        # `__lime__` declared directly on this class is the registration.
        # `vars(cls)` rather than `cls.__lime__` so subclasses do not
        # re-register under their parent's path.
        path = vars(cls).get("__lime__")
        if path:
            registry.register(path, cls)
