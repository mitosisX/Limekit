"""Spec collection and accessor generation.

Uses __init_subclass__ rather than a metaclass: type(QWidget) is a Shiboken
metaclass, and a naive `class Meta(type)` raises a metaclass conflict.
"""

from limekit.kernel.spec import Prop, Event, Method

_SPEC_TYPES = (Prop, Event, Method)


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
