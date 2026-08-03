"""Spike 2: does declaring `text = Prop(...)` shadow QPushButton.text()?

If so, does delattr() during __init_subclass__ restore it cleanly?
This is load-bearing for the whole declarative design.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QPushButton
from PySide6.QtGui import QIcon

app = QApplication([])
r = {}


class Prop:
    def __init__(self, type_, *, default=None, qt=None, coerce=None):
        self.type, self.default, self.qt, self.coerce = type_, default, qt, coerce
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name


class Event:
    def __init__(self, qt_signal, *, passes_self=True):
        self.qt_signal, self.passes_self = qt_signal, passes_self
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name


# --- A. WITHOUT cleanup: prove the shadowing hazard is real ------------------
class Shadowed(QPushButton):
    text = Prop(str, qt=("text", "setText"))


try:
    s = Shadowed()
    got = s.text
    r["A_shadow_hazard"] = (
        f"SHADOWED -> s.text is {type(got).__name__} "
        f"(callable={callable(got)}) -- confirms cleanup is REQUIRED"
    )
except Exception as e:
    r["A_shadow_hazard"] = f"raised {type(e).__name__}: {e}"


# --- B. WITH cleanup via delattr in __init_subclass__ ------------------------
class LimeBase:
    __props__ = ()
    __events__ = ()

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        props, events, drop = {}, {}, []

        for base in reversed(cls.__mro__):
            for k, v in vars(base).items():
                if isinstance(v, Prop):
                    props[k] = v
                elif isinstance(v, Event):
                    events[k] = v

        # remove the spec objects from THIS class so Qt's own attrs resurface
        for k, v in list(vars(cls).items()):
            if isinstance(v, (Prop, Event)):
                drop.append(k)
        for k in drop:
            delattr(cls, k)

        cls.__props__ = tuple(props.values())
        cls.__events__ = tuple(events.values())
        for p in props.values():
            _install_prop(cls, p)
        for e in events.values():
            _install_event(cls, e)


def _install_prop(cls, p):
    cap = p.name[0].upper() + p.name[1:]
    coerce = p.coerce

    # CRITICAL: resolve the Qt functions NOW, before setattr can shadow them.
    # A Prop named `text` generates `setText`, which would otherwise overwrite
    # QPushButton.setText and then recurse into itself.
    qt_get_fn = getattr(cls, p.qt[0])
    qt_set_fn = getattr(cls, p.qt[1])

    def getter(self, _g=qt_get_fn):
        return _g(self)

    def setter(self, value, _s=qt_set_fn, _c=coerce):
        return _s(self, _c(value) if _c else value)

    getter.__name__, setter.__name__ = f"get{cap}", f"set{cap}"
    setattr(cls, f"get{cap}", getter)
    setattr(cls, f"set{cap}", setter)


def _install_event(cls, e):
    cap = e.name[0].upper() + e.name[1:]

    def attach(self, fn, _sig=e.qt_signal, _self=e.passes_self):
        def guarded(*a):
            try:
                return fn(self) if _self else fn()
            except Exception as ex:                       # noqa: BLE001
                print(f"  [guard] caught {type(ex).__name__}: {ex}")
        getattr(self, _sig).connect(guarded)

    attach.__name__ = f"set{cap}"
    setattr(cls, f"set{cap}", attach)


class Button(LimeBase, QPushButton):
    text    = Prop(str,  default="Button", qt=("text", "setText"), coerce=str)
    icon    = Prop(QIcon, qt=("icon", "setIcon"), coerce=QIcon)
    flat    = Prop(bool, default=False, qt=("isFlat", "setFlat"))
    checked = Prop(bool, default=False, qt=("isChecked", "setChecked"))
    onClick = Event("clicked", passes_self=True)

    def __init__(self, text="Button"):
        super().__init__()
        self.setText(text)


try:
    b = Button("hi")
    b.setFlat(True)
    b.setCheckable(True)
    b.setChecked(True)
    r["B_cleanup_restores_qt"] = (
        f"OK  b.text is {type(b.text).__name__} callable={callable(b.text)} "
        f"| getText()={b.getText()!r} getFlat()={b.getFlat()!r} "
        f"getChecked()={b.getChecked()!r}"
    )
except Exception as e:
    r["B_cleanup_restores_qt"] = f"FAIL {type(e).__name__}: {e}"

# coercion actually applied?
try:
    b2 = Button()
    b2.setText(42)
    r["C_coercion"] = f"OK  setText(42) -> {b2.getText()!r} (type {type(b2.getText()).__name__})"
except Exception as e:
    r["C_coercion"] = f"FAIL {type(e).__name__}: {e}"

# event guard: does a raising handler stay contained?
try:
    b3 = Button()
    b3.setOnClick(lambda self: 1 / 0)
    b3.click()
    r["D_guard_contains"] = "OK  exception contained, click() returned normally"
except Exception as e:
    r["D_guard_contains"] = f"FAIL escaped: {type(e).__name__}: {e}"


# --- E. subclass overriding a parent Prop -----------------------------------
class FancyButton(Button):
    text = Prop(str, default="Fancy", qt=("text", "setText"), coerce=lambda v: f">> {v}")


try:
    f = FancyButton()
    f.setText("x")
    r["E_subclass_override"] = (
        f"OK  FancyButton.setText('x') -> {f.getText()!r} "
        f"| inherited getFlat present={hasattr(f, 'getFlat')}"
    )
except Exception as e:
    r["E_subclass_override"] = f"FAIL {type(e).__name__}: {e}"


# --- F. does the parent still work after the subclass redefined the prop? ---
try:
    b4 = Button()
    b4.setText("plain")
    r["F_parent_unaffected"] = f"OK  Button.setText('plain') -> {b4.getText()!r}"
except Exception as e:
    r["F_parent_unaffected"] = f"FAIL {type(e).__name__}: {e}"

for k in sorted(r):
    print(f"{k:24} {r[k]}")
