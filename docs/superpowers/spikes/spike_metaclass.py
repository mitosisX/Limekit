"""Spike: does declarative metadata survive Shiboken + lupa?

Validates the P0 kernel's riskiest assumption before designing on it.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QPushButton, QLineEdit
import lupa
from lupa import LuaRuntime

app = QApplication([])
results = {}


# --- 1. __init_subclass__ on a mixin, combined with a Shiboken base -----------
REGISTRY = {}


class Prop:
    """Inert spec object. Not a descriptor - read at class-creation time."""

    def __init__(self, name, default=None, qt_getter=None, qt_setter=None):
        self.name = name
        self.default = default
        self.qt_getter = qt_getter
        self.qt_setter = qt_setter


class LimeBase:
    __props__ = ()
    __lime_name__ = None

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        collected = []
        for base in reversed(cls.__mro__):
            collected.extend(getattr(base, "__declared_props__", ()))
        cls.__props__ = tuple(collected)
        # install generated accessors
        for p in collected:
            _install(cls, p)
        name = cls.__lime_name__ or cls.__name__
        REGISTRY[name] = cls


def _install(cls, p):
    cap = p.name[0].upper() + p.name[1:]
    getter_name, setter_name = f"get{cap}", f"set{cap}"
    qt_get, qt_set = p.qt_getter, p.qt_setter

    if not hasattr(cls, getter_name):
        def getter(self, _qt_get=qt_get):
            return getattr(self, _qt_get)()
        getter.__name__ = getter_name
        setattr(cls, getter_name, getter)

    if not hasattr(cls, setter_name):
        def setter(self, value, _qt_set=qt_set):
            return getattr(self, _qt_set)(value)
        setter.__name__ = setter_name
        setattr(cls, setter_name, setter)


class Button(LimeBase, QPushButton):
    __declared_props__ = (Prop("text", "Button", "text", "setText"),)

    def __init__(self, text="Button"):
        super().__init__()
        self.setText(text)


class LineEdit(LimeBase, QLineEdit):
    __declared_props__ = (
        Prop("text", "", "text", "setText"),
        Prop("placeholder", "", "placeholderText", "setPlaceholderText"),
    )


try:
    b = Button("hello")
    results["1_init_subclass_mi"] = (
        f"OK  registry={sorted(REGISTRY)} "
        f"Button.getText()={b.getText()!r} props={[p.name for p in Button.__props__]}"
    )
except Exception as e:
    results["1_init_subclass_mi"] = f"FAIL {type(e).__name__}: {e}"

try:
    le = LineEdit()
    le.setPlaceholder("type here")
    results["2_generated_accessors"] = (
        f"OK  getPlaceholder()={le.getPlaceholder()!r} "
        f"props={[p.name for p in LineEdit.__props__]}"
    )
except Exception as e:
    results["2_generated_accessors"] = f"FAIL {type(e).__name__}: {e}"


# --- 3. true descriptor (__get__/__set__) on a Shiboken subclass -------------
class DescProp:
    def __set_name__(self, owner, name):
        self._n = "_" + name

    def __get__(self, obj, owner=None):
        if obj is None:
            return self
        return getattr(obj, self._n, None)

    def __set__(self, obj, value):
        setattr(obj, self._n, value)


class DescButton(QPushButton):
    tag = DescProp()


try:
    db = DescButton()
    db.tag = "primary"
    results["3_descriptor_on_qwidget"] = f"OK  tag={db.tag!r}"
except Exception as e:
    results["3_descriptor_on_qwidget"] = f"FAIL {type(e).__name__}: {e}"


# --- 4. custom metaclass on a Shiboken subclass (the risky alternative) ------
try:
    class LimeMeta(type(QPushButton)):
        def __new__(mcls, name, bases, ns, **kw):
            return super().__new__(mcls, name, bases, ns, **kw)

    class MetaButton(QPushButton, metaclass=LimeMeta):
        pass

    MetaButton()
    results["4_custom_metaclass"] = "OK  (works, but must subclass type(QPushButton))"
except Exception as e:
    results["4_custom_metaclass"] = f"FAIL {type(e).__name__}: {e}"

# 4b. the naive version people write first
try:
    class NaiveMeta(type):
        pass

    class NaiveButton(QPushButton, metaclass=NaiveMeta):
        pass

    results["4b_naive_metaclass"] = "OK"
except Exception as e:
    results["4b_naive_metaclass"] = f"FAIL {type(e).__name__}: {e}"


# --- 5. do generated methods reach Lua through lupa? ------------------------
try:
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.globals()["Button"] = Button
    out = lua.eval('(function() local b = Button("from lua") return b:getText() end)()')
    results["5_lua_sees_generated"] = f"OK  lua got {out!r}"
except Exception as e:
    results["5_lua_sees_generated"] = f"FAIL {type(e).__name__}: {e}"


# --- 6. namespaced module table instead of 150 flat globals -----------------
try:
    lua2 = LuaRuntime(unpack_returned_tuples=True)
    ui = lua2.table_from({k: v for k, v in REGISTRY.items()})
    lua2.globals()["__lime_ui"] = ui
    out = lua2.eval(
        '(function() local ui = __lime_ui '
        'local b = ui.Button("ns") return b:getText() end)()'
    )
    results["6_namespaced_modules"] = f"OK  lua got {out!r}"
except Exception as e:
    results["6_namespaced_modules"] = f"FAIL {type(e).__name__}: {e}"


# --- 7. is the lupa runtime usable from another thread? --------------------
import threading

try:
    lua3 = LuaRuntime(unpack_returned_tuples=True)
    lua3.execute("counter = 0")
    err = []

    def worker():
        try:
            lua3.execute("counter = counter + 1")
        except Exception as e:                      # noqa: BLE001
            err.append(f"{type(e).__name__}: {e}")

    ts = [threading.Thread(target=worker) for _ in range(8)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    results["7_lua_cross_thread"] = (
        f"counter={lua3.eval('counter')} errors={err[:2] or 'none'}"
    )
except Exception as e:
    results["7_lua_cross_thread"] = f"FAIL {type(e).__name__}: {e}"


# --- 8. can a Lua table subclass / extend a Python widget? (component model) -
try:
    lua4 = LuaRuntime(unpack_returned_tuples=True)
    lua4.globals()["Button"] = Button
    out = lua4.eval("""
        (function()
            local b = Button("base")
            -- can lua attach its own fields to the python object?
            local ok, err = pcall(function() b.customField = 42 end)
            return tostring(ok) .. "|" .. tostring(err)
        end)()
    """)
    results["8_lua_attach_field"] = f"OK  {out!r}"
except Exception as e:
    results["8_lua_attach_field"] = f"FAIL {type(e).__name__}: {e}"


for k in sorted(results):
    print(f"{k:28} {results[k]}")
