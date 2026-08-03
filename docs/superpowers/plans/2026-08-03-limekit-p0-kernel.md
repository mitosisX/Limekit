# Limekit 2.0 — P0 Kernel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Limekit's path-based class discovery, hand-written Lua bindings and import-time side effects with a declarative metadata kernel that generates accessors, bindings, stubs and the frozen-mode manifest from one source of truth.

**Architecture:** Widgets declare `Prop`/`Event`/`Method` spec objects in their class body. `__init_subclass__` collects them across the MRO, deletes the spec objects so Qt attributes resurface, and installs generated accessors with Qt methods bound at generation time. A registry indexes every class by dotted path; generators walk it to emit `limekit.lua`, LSP stubs and `manifest.py`. All Lua callbacks cross a single guard. `LimekitApp` owns the lifecycle explicitly.

**Tech Stack:** Python 3.10+, PySide6 6.11.0, lupa 2.8, pytest, pytest-qt, import-linter

**Spec:** `docs/superpowers/specs/2026-08-03-limekit-p0-kernel-design.md`
**Branch:** `limekit-2.0`

## Execution Order

**Tasks are numbered by topic but executed in this order:**

```
1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 16 → 12 → 13 → 14 → 15 → 17
                                              ↑
                            pilot widgets run BEFORE the generators
```

Task 16 (pilot widgets) creates the first classes carrying `__lime__`. The three
generators (12 manifest, 13 `limekit.lua`, 14 stubs) assert over a non-empty registry,
so running them first would either fail outright or pass vacuously. Task 16 moves ahead
of them; nothing else changes.

## Global Constraints

Every task's requirements implicitly include this section.

- **Never use a custom metaclass.** `type(QWidget)` is a Shiboken metaclass; a naive `class Meta(type)` raises `TypeError: metaclass conflict`. Use `__init_subclass__`.
- **Constraint C1 — delete spec objects after collecting.** `text = Prop(...)` shadows `QPushButton.text`. The collector must `delattr` every `Prop`/`Event`/`Method` from the class, or the Qt attribute stays hidden.
- **Constraint C2 — bind Qt methods at generation time.** A `Prop` named `text` generates `setText`, colliding with the Qt method it calls. `getattr(self, "setText")` at call time resolves to itself and recurses. Resolve with `getattr(cls, name)` *before* any `setattr`.
- **`kernel/` imports nothing from `widgets/`, `services/` or `toolkit/`.** Enforced by Task 15.
- **The Lua API is 1-indexed everywhere.** Conversion happens via the `LuaIndex` coercion, never by ad-hoc `- 1` arithmetic in methods.
- **Generated files are committed**, and regeneration must be a verified no-op in CI.
- **No Python builtins in Lua globals.** No `eval`, `str`, `int`, `dict`, `tuple`, `print`, `len`.
- Tests run headless: `QT_QPA_PLATFORM=offscreen`.

---

### Task 1: Test harness and dependency repair

There are currently zero tests, and `app_engine.py:11` imports `playsound`, which is absent from `requirements.txt`. `setup.py` and `requirements.txt` also disagree. Fix both so a clean checkout can install and test.

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/test_harness.py`
- Create: `pytest.ini`
- Modify: `requirements.txt`
- Modify: `setup.py`

**Interfaces:**
- Consumes: nothing
- Produces: `qapp` pytest fixture (session-scoped `QApplication`); `pytest` runnable from repo root

- [ ] **Step 1: Write the failing test**

```python
# tests/test_harness.py
import os


def test_offscreen_platform_is_set():
    assert os.environ["QT_QPA_PLATFORM"] == "offscreen"


def test_qapplication_available(qapp):
    from PySide6.QtWidgets import QApplication
    assert isinstance(qapp, QApplication)


def test_declared_dependencies_are_importable():
    """Every module limekit imports at runtime must be installable."""
    import importlib
    for mod in ("PySide6", "lupa", "playsound", "psutil", "emoji"):
        importlib.import_module(mod)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_harness.py -v`
Expected: FAIL — `pytest.ini` and `conftest.py` do not exist, so there is no `qapp` fixture and `QT_QPA_PLATFORM` is unset.

- [ ] **Step 3: Write minimal implementation**

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -q
```

```python
# tests/conftest.py
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app
```

Add to `requirements.txt` (it is missing `playsound`, which `app_engine.py:11` imports):

```
PySide6
lupa
playsound
psutil
emoji
pyqtdarktheme
qdarkstyle
qt_material
qtmodern
pytest
pytest-qt
import-linter
```

In `setup.py`, replace the `install_requires` list so it matches `requirements.txt`, and drop `PyInstaller` (it is a build tool, not a runtime dependency):

```python
    install_requires=[
        "PySide6",
        "lupa",
        "playsound",
        "psutil",
        "emoji",
        "pyqtdarktheme",
        "qdarkstyle",
        "qt_material",
        "qtmodern",
    ],
    extras_require={
        "build": ["PyInstaller"],
        "dev": ["pytest", "pytest-qt", "import-linter"],
    },
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_harness.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add pytest.ini tests/conftest.py tests/test_harness.py requirements.txt setup.py
git commit -m "test: add headless pytest harness and reconcile dependencies"
```

---

### Task 2: Error taxonomy

Replaces the 10-branch `except` ladder in `runner.py` with dispatch on a type.

**Files:**
- Create: `limekit/kernel/__init__.py`
- Create: `limekit/kernel/errors.py`
- Create: `tests/kernel/test_errors.py`

**Interfaces:**
- Consumes: nothing
- Produces: `LimekitError`, `BridgeError`, `RegistryError`, `ProjectError`, `RouteError`, `LuaError`, `WidgetCallbackError`. `LuaError` carries `.source` (str) and `.line` (int|None). `WidgetCallbackError` carries `.widget` (str) and `.event` (str).

- [ ] **Step 1: Write the failing test**

```python
# tests/kernel/test_errors.py
import pytest
from limekit.kernel.errors import (
    LimekitError, BridgeError, RegistryError, ProjectError,
    RouteError, LuaError, WidgetCallbackError,
)


@pytest.mark.parametrize("cls", [
    BridgeError, RegistryError, ProjectError, RouteError,
    LuaError, WidgetCallbackError,
])
def test_all_errors_share_a_root(cls):
    assert issubclass(cls, LimekitError)


def test_lua_error_carries_source_and_line():
    err = LuaError("bad syntax", source="scripts/main.lua", line=47)
    assert err.source == "scripts/main.lua"
    assert err.line == 47
    assert "scripts/main.lua:47" in str(err)


def test_lua_error_without_line_omits_it():
    err = LuaError("boom", source="scripts/main.lua")
    assert err.line is None
    assert "scripts/main.lua" in str(err)
    assert ":None" not in str(err)


def test_widget_callback_error_names_widget_and_event():
    err = WidgetCallbackError("handler failed", widget="Button", event="onClick")
    assert err.widget == "Button"
    assert err.event == "onClick"
    assert "Button.onClick" in str(err)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/kernel/test_errors.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'limekit.kernel'`

- [ ] **Step 3: Write minimal implementation**

```python
# limekit/kernel/__init__.py
```

```python
# limekit/kernel/errors.py
"""Exception taxonomy for the Limekit kernel.

Replaces the per-exception-type ladder in the old runner with a hierarchy
that callers can dispatch on.
"""


class LimekitError(Exception):
    """Root of every error Limekit raises deliberately."""


class BridgeError(LimekitError):
    """A value could not be marshalled between Lua and Python."""


class RegistryError(LimekitError):
    """A class could not be registered, or a lookup failed."""


class ProjectError(LimekitError):
    """The project on disk is missing or malformed."""


class RouteError(LimekitError):
    """A route could not be resolved to a resource."""


class LuaError(LimekitError):
    """Lua raised, or failed to compile.

    Carries the originating source file and line so callers never have to
    parse them back out of a message string.
    """

    def __init__(self, message, *, source="<unknown>", line=None):
        self.source = source
        self.line = line
        location = f"{source}:{line}" if line is not None else source
        super().__init__(f"{location}: {message}")


class WidgetCallbackError(LimekitError):
    """A Lua handler attached to a widget event raised."""

    def __init__(self, message, *, widget, event):
        self.widget = widget
        self.event = event
        super().__init__(f"{widget}.{event}: {message}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/kernel/test_errors.py -v`
Expected: PASS (9 tests)

- [ ] **Step 5: Commit**

```bash
git add limekit/kernel/ tests/kernel/
git commit -m "feat(kernel): add error taxonomy"
```

---

### Task 3: Spec objects

Inert data describing a widget's surface. No descriptor protocol beyond `__set_name__`, which only records the attribute name.

**Files:**
- Create: `limekit/kernel/spec.py`
- Create: `tests/kernel/test_spec.py`

**Interfaces:**
- Consumes: nothing
- Produces:
  - `Prop(type_, *, default=None, qt=None, coerce=None, validate=None, doc="", lua_name=None)` with attributes `.name .type .default .qt .coerce .validate .doc .lua_name`, and `.accessor_names()` → `(getter, setter, alias_or_None)`
  - `Event(qt_signal, *, passes_self=True, args=(), doc="")` with `.name .qt_signal .passes_self .args .doc`, and `.setter_name()` → str
  - `Method(*, qt=None, doc="", lua_name=None)` with `.name .qt .doc .lua_name`

- [ ] **Step 1: Write the failing test**

```python
# tests/kernel/test_spec.py
import pytest
from limekit.kernel.spec import Prop, Event, Method


def test_prop_records_its_attribute_name():
    class Holder:
        text = Prop(str, qt=("text", "setText"))
    assert Holder.text.name == "text"


def test_prop_accessor_names():
    p = Prop(str, qt=("text", "setText"))
    p.name = "text"
    assert p.accessor_names() == ("getText", "setText", None)


def test_bool_prop_gets_an_is_alias():
    p = Prop(bool, qt=("isFlat", "setFlat"))
    p.name = "flat"
    assert p.accessor_names() == ("getFlat", "setFlat", "isFlat")


def test_lua_name_overrides_the_generated_names():
    p = Prop(str, qt=("text", "setText"), lua_name="caption")
    p.name = "text"
    assert p.accessor_names() == ("getCaption", "setCaption", None)


def test_prop_requires_a_qt_pair():
    with pytest.raises(ValueError, match="qt"):
        Prop(str)


def test_event_setter_name():
    e = Event("clicked")
    e.name = "onClick"
    assert e.setter_name() == "setOnClick"


def test_event_defaults_to_passing_self():
    assert Event("clicked").passes_self is True


def test_method_records_its_name():
    class Holder:
        center = Method(qt="center")
    assert Holder.center.name == "center"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/kernel/test_spec.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'limekit.kernel.spec'`

- [ ] **Step 3: Write minimal implementation**

```python
# limekit/kernel/spec.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/kernel/test_spec.py -v`
Expected: PASS (8 tests)

- [ ] **Step 5: Commit**

```bash
git add limekit/kernel/spec.py tests/kernel/test_spec.py
git commit -m "feat(kernel): add Prop, Event and Method spec objects"
```

---

### Task 4: Coercion vocabulary

Collapses the alignment, cursor, dock-area and size-policy lookup tables currently re-declared and divergent across `BaseLayout`, `Label`, `Window` and `ComboBox`. Note `label.py:105,107` defines `"openhand"` twice and maps `"wait"` to `ArrowCursor`; the shared maps here fix both.

**Files:**
- Create: `limekit/kernel/coerce.py`
- Create: `tests/kernel/test_coerce.py`

**Interfaces:**
- Consumes: `limekit.kernel.errors.BridgeError`
- Produces: `Icon(v)`, `Size(v)`, `Colour(v)`, `LuaIndex(v)`, `Enum(mapping, label)` factory returning a callable, and the shared maps `ALIGNMENTS`, `CURSORS`, `DOCK_AREAS`, `TOOLBAR_AREAS`, `SIZE_POLICIES`

- [ ] **Step 1: Write the failing test**

```python
# tests/kernel/test_coerce.py
import pytest
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QColor
from limekit.kernel.coerce import (
    Icon, Size, Colour, LuaIndex, Enum,
    ALIGNMENTS, CURSORS, SIZE_POLICIES,
)
from limekit.kernel.errors import BridgeError


def test_icon_from_path(qapp):
    assert isinstance(Icon("nonexistent.png"), QIcon)


def test_icon_passes_through_an_existing_icon(qapp):
    original = QIcon()
    assert Icon(original) is original


def test_size_from_pair(qapp):
    assert Size((800, 600)) == QSize(800, 600)


def test_colour_from_hex(qapp):
    assert Colour("#ff0000") == QColor(255, 0, 0)


def test_lua_index_is_one_based():
    assert LuaIndex(1) == 0
    assert LuaIndex(5) == 4


def test_lua_index_rejects_zero():
    with pytest.raises(BridgeError, match="1-indexed"):
        LuaIndex(0)


def test_enum_is_case_insensitive():
    align = Enum(ALIGNMENTS, "alignment")
    assert align("CENTER") == Qt.AlignmentFlag.AlignCenter
    assert align("center") == Qt.AlignmentFlag.AlignCenter


def test_enum_rejects_unknown_and_lists_options():
    align = Enum(ALIGNMENTS, "alignment")
    with pytest.raises(BridgeError) as exc:
        align("sideways")
    assert "sideways" in str(exc.value)
    assert "center" in str(exc.value)


def test_cursor_map_has_no_duplicate_targets_for_openhand():
    """label.py defined 'openhand' twice; the second silently won."""
    assert CURSORS["openhand"] == Qt.CursorShape.OpenHandCursor


def test_wait_cursor_is_actually_a_wait_cursor():
    """label.py mapped 'wait' to ArrowCursor."""
    assert CURSORS["wait"] == Qt.CursorShape.WaitCursor


def test_size_policies_are_complete():
    assert set(SIZE_POLICIES) == {
        "fixed", "expanding", "ignore", "maximum",
        "minimum", "minimumexpanding", "preferred",
    }
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/kernel/test_coerce.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'limekit.kernel.coerce'`

- [ ] **Step 3: Write minimal implementation**

```python
# limekit/kernel/coerce.py
"""Coercions a Prop names via `coerce=`.

One shared table per Qt enum, replacing the divergent copies previously
spread across BaseLayout, Label, Window and ComboBox.
"""

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QColor
from PySide6.QtWidgets import QSizePolicy

from limekit.kernel.errors import BridgeError


def Icon(value):
    if isinstance(value, QIcon):
        return value
    return QIcon(value)


def Size(value):
    if isinstance(value, QSize):
        return value
    try:
        width, height = value
    except (TypeError, ValueError) as exc:
        raise BridgeError(f"expected a {{width, height}} pair, got {value!r}") from exc
    return QSize(int(width), int(height))


def Colour(value):
    if isinstance(value, QColor):
        return value
    if isinstance(value, (tuple, list)):
        return QColor(*(int(c) for c in value))
    return QColor(value)


def LuaIndex(value):
    """Lua is 1-indexed; Qt is 0-indexed. Convert at the boundary."""
    index = int(value)
    if index < 1:
        raise BridgeError(
            f"index {index} is out of range - the Limekit API is 1-indexed"
        )
    return index - 1


def Enum(mapping, label):
    """Build a case-insensitive string -> Qt enum coercion."""

    def coerce(value):
        if not isinstance(value, str):
            return value
        try:
            return mapping[value.lower()]
        except KeyError:
            options = ", ".join(sorted(mapping))
            raise BridgeError(
                f"unknown {label} {value!r}; expected one of: {options}"
            ) from None

    coerce.__name__ = f"coerce_{label}"
    coerce.options = tuple(sorted(mapping))
    return coerce


ALIGNMENTS = {
    "left": Qt.AlignmentFlag.AlignLeft,
    "right": Qt.AlignmentFlag.AlignRight,
    "top": Qt.AlignmentFlag.AlignTop,
    "bottom": Qt.AlignmentFlag.AlignBottom,
    "center": Qt.AlignmentFlag.AlignCenter,
    "hcenter": Qt.AlignmentFlag.AlignHCenter,
    "vcenter": Qt.AlignmentFlag.AlignVCenter,
    "justify": Qt.AlignmentFlag.AlignJustify,
    "baseline": Qt.AlignmentFlag.AlignBaseline,
    "leading": Qt.AlignmentFlag.AlignLeading,
    "trailing": Qt.AlignmentFlag.AlignTrailing,
}

CURSORS = {
    "arrow": Qt.CursorShape.ArrowCursor,
    "uparrow": Qt.CursorShape.UpArrowCursor,
    "wait": Qt.CursorShape.WaitCursor,
    "busy": Qt.CursorShape.BusyCursor,
    "cross": Qt.CursorShape.CrossCursor,
    "ibeam": Qt.CursorShape.IBeamCursor,
    "sizever": Qt.CursorShape.SizeVerCursor,
    "sizehor": Qt.CursorShape.SizeHorCursor,
    "sizebdiag": Qt.CursorShape.SizeBDiagCursor,
    "sizefdiag": Qt.CursorShape.SizeFDiagCursor,
    "sizeall": Qt.CursorShape.SizeAllCursor,
    "blank": Qt.CursorShape.BlankCursor,
    "splitv": Qt.CursorShape.SplitVCursor,
    "splith": Qt.CursorShape.SplitHCursor,
    "pointinghand": Qt.CursorShape.PointingHandCursor,
    "forbidden": Qt.CursorShape.ForbiddenCursor,
    "whatsthis": Qt.CursorShape.WhatsThisCursor,
    "openhand": Qt.CursorShape.OpenHandCursor,
    "closedhand": Qt.CursorShape.ClosedHandCursor,
    "dragcopy": Qt.CursorShape.DragCopyCursor,
    "dragmove": Qt.CursorShape.DragMoveCursor,
    "draglink": Qt.CursorShape.DragLinkCursor,
    "custom": Qt.CursorShape.CustomCursor,
}

DOCK_AREAS = {
    "left": Qt.DockWidgetArea.LeftDockWidgetArea,
    "right": Qt.DockWidgetArea.RightDockWidgetArea,
    "top": Qt.DockWidgetArea.TopDockWidgetArea,
    "bottom": Qt.DockWidgetArea.BottomDockWidgetArea,
    "all": Qt.DockWidgetArea.AllDockWidgetAreas,
    "none": Qt.DockWidgetArea.NoDockWidgetArea,
}

TOOLBAR_AREAS = {
    "left": Qt.ToolBarArea.LeftToolBarArea,
    "right": Qt.ToolBarArea.RightToolBarArea,
    "top": Qt.ToolBarArea.TopToolBarArea,
    "bottom": Qt.ToolBarArea.BottomToolBarArea,
}

SIZE_POLICIES = {
    "fixed": QSizePolicy.Policy.Fixed,
    "expanding": QSizePolicy.Policy.Expanding,
    "ignore": QSizePolicy.Policy.Ignored,
    "maximum": QSizePolicy.Policy.Maximum,
    "minimum": QSizePolicy.Policy.Minimum,
    "minimumexpanding": QSizePolicy.Policy.MinimumExpanding,
    "preferred": QSizePolicy.Policy.Preferred,
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/kernel/test_coerce.py -v`
Expected: PASS (11 tests)

- [ ] **Step 5: Commit**

```bash
git add limekit/kernel/coerce.py tests/kernel/test_coerce.py
git commit -m "feat(kernel): add shared coercion vocabulary and Qt enum maps"
```

---

### Task 5: Declarative collector

Implements constraint C1. Walks the MRO, collects specs, and removes them from the class so Qt attributes resurface.

**Files:**
- Create: `limekit/kernel/declarative.py`
- Create: `tests/kernel/test_declarative_collect.py`

**Interfaces:**
- Consumes: `limekit.kernel.spec.Prop/Event/Method`
- Produces: `LimeObject` base class exposing `__props__`, `__events__`, `__methods__` as tuples, and `__lime__` (str|None). Accessor generation arrives in Task 6; this task collects only.

- [ ] **Step 1: Write the failing test**

```python
# tests/kernel/test_declarative_collect.py
from PySide6.QtWidgets import QPushButton
from limekit.kernel.declarative import LimeObject
from limekit.kernel.spec import Prop, Event


def test_specs_are_collected(qapp):
    class W(LimeObject, QPushButton):
        text = Prop(str, qt=("text", "setText"))
        onClick = Event("clicked")

    assert [p.name for p in W.__props__] == ["text"]
    assert [e.name for e in W.__events__] == ["onClick"]


def test_spec_objects_are_removed_from_the_class(qapp):
    """Constraint C1: `text = Prop(...)` shadows QPushButton.text."""
    class W(LimeObject, QPushButton):
        text = Prop(str, qt=("text", "setText"))

    assert "text" not in vars(W)
    assert callable(W().text)          # QPushButton.text resurfaced


def test_subclasses_inherit_parent_specs(qapp):
    class Base(LimeObject, QPushButton):
        text = Prop(str, qt=("text", "setText"))

    class Child(Base):
        flat = Prop(bool, qt=("isFlat", "setFlat"))

    assert {p.name for p in Child.__props__} == {"text", "flat"}


def test_subclass_may_override_a_parent_prop(qapp):
    class Base(LimeObject, QPushButton):
        text = Prop(str, qt=("text", "setText"), doc="base")

    class Child(Base):
        text = Prop(str, qt=("text", "setText"), doc="child")

    docs = {p.name: p.doc for p in Child.__props__}
    assert docs["text"] == "child"
    assert len(Child.__props__) == 1        # overridden, not duplicated


def test_overriding_does_not_corrupt_the_parent(qapp):
    class Base(LimeObject, QPushButton):
        text = Prop(str, qt=("text", "setText"), doc="base")

    class Child(Base):
        text = Prop(str, qt=("text", "setText"), doc="child")

    assert {p.doc for p in Base.__props__} == {"base"}


def test_lime_path_is_recorded(qapp):
    class W(LimeObject, QPushButton):
        __lime__ = "ui.Thing"

    assert W.__lime__ == "ui.Thing"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/kernel/test_declarative_collect.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'limekit.kernel.declarative'`

- [ ] **Step 3: Write minimal implementation**

```python
# limekit/kernel/declarative.py
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
        for base in reversed(cls.__mro__):
            for key, value in vars(base).items():
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/kernel/test_declarative_collect.py -v`
Expected: PASS (6 tests)

- [ ] **Step 5: Commit**

```bash
git add limekit/kernel/declarative.py tests/kernel/test_declarative_collect.py
git commit -m "feat(kernel): collect specs across the MRO and unshadow Qt attrs"
```

---

### Task 6: Property accessor generation

Implements constraint C2. Qt functions are resolved before any `setattr`, because a `Prop` named `text` generates a `setText` that would otherwise overwrite and then recurse into `QPushButton.setText`.

**Files:**
- Modify: `limekit/kernel/declarative.py`
- Create: `tests/kernel/test_declarative_props.py`

**Interfaces:**
- Consumes: Task 5's `LimeObject`, Task 3's `Prop.accessor_names()`
- Produces: for every `Prop`, generated `get<Name>` / `set<Name>` (plus `is<Name>` for bools) installed on the class

- [ ] **Step 1: Write the failing test**

```python
# tests/kernel/test_declarative_props.py
import pytest
from PySide6.QtWidgets import QPushButton
from limekit.kernel.declarative import LimeObject
from limekit.kernel.spec import Prop
from limekit.kernel.errors import BridgeError


@pytest.fixture
def Button(qapp):
    class Button(LimeObject, QPushButton):
        text = Prop(str, default="Button", qt=("text", "setText"), coerce=str)
        flat = Prop(bool, default=False, qt=("isFlat", "setFlat"))
    return Button


def test_accessors_are_generated(Button):
    b = Button()
    assert hasattr(b, "getText") and hasattr(b, "setText")


def test_setter_does_not_recurse(Button):
    """Constraint C2: setText must call QPushButton.setText, not itself."""
    b = Button()
    b.setText("hello")
    assert b.getText() == "hello"


def test_coercion_is_applied(Button):
    b = Button()
    b.setText(42)
    assert b.getText() == "42"


def test_bool_props_get_an_is_alias(Button):
    b = Button()
    b.setFlat(True)
    assert b.isFlat() is True
    assert b.getFlat() is True


def test_validate_rejects_bad_values(qapp):
    class W(LimeObject, QPushButton):
        text = Prop(str, qt=("text", "setText"),
                    validate=lambda v: len(v) <= 3)

    w = W()
    w.setText("ok")
    with pytest.raises(BridgeError, match="text"):
        w.setText("far too long")


def test_generated_setter_returns_self_for_chaining(Button):
    b = Button()
    assert b.setText("x") is b
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/kernel/test_declarative_props.py -v`
Expected: FAIL with `AttributeError: 'Button' object has no attribute 'getText'`

- [ ] **Step 3: Write minimal implementation**

Add the import and the generator to `limekit/kernel/declarative.py`, and call it from `__init_subclass__`:

```python
from limekit.kernel.errors import BridgeError
```

```python
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
```

At the end of `__init_subclass__`, after the three `cls.__*__` assignments:

```python
        for prop in cls.__props__:
            _install_prop(cls, prop)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/kernel/ -v`
Expected: PASS (all kernel tests, including Task 5's)

- [ ] **Step 5: Commit**

```bash
git add limekit/kernel/declarative.py tests/kernel/test_declarative_props.py
git commit -m "feat(kernel): generate property accessors with Qt methods bound early"
```

---

### Task 7: Guarded event accessors

Today `Button` wraps callbacks in try/except while `ComboBox`, `ListBox`, `Label` and every `Window` event do not. After this task there is no unguarded path to attach a handler.

**Files:**
- Create: `limekit/kernel/bridge/__init__.py`
- Create: `limekit/kernel/bridge/guard.py`
- Modify: `limekit/kernel/declarative.py`
- Create: `tests/kernel/test_guard.py`

**Interfaces:**
- Consumes: `WidgetCallbackError`, Task 5's `LimeObject`
- Produces:
  - `guard(fn, *, widget, event, on_error=None)` → wrapped callable that never raises
  - `set_error_sink(callable)` / `reset_error_sink()` for tests and for the app to route errors
  - generated `setOn<Name>` for every `Event`

- [ ] **Step 1: Write the failing test**

```python
# tests/kernel/test_guard.py
import pytest
from PySide6.QtWidgets import QPushButton
from limekit.kernel.bridge.guard import guard, set_error_sink, reset_error_sink
from limekit.kernel.declarative import LimeObject
from limekit.kernel.spec import Event
from limekit.kernel.errors import WidgetCallbackError


@pytest.fixture(autouse=True)
def sink():
    captured = []
    set_error_sink(captured.append)
    yield captured
    reset_error_sink()


def test_guard_contains_exceptions(sink):
    wrapped = guard(lambda: 1 / 0, widget="Button", event="onClick")
    wrapped()                                    # must not raise
    assert len(sink) == 1
    assert isinstance(sink[0], WidgetCallbackError)


def test_guard_names_the_widget_and_event(sink):
    wrapped = guard(lambda: 1 / 0, widget="ComboBox", event="onItemSelect")
    wrapped()
    assert sink[0].widget == "ComboBox"
    assert sink[0].event == "onItemSelect"


def test_guard_passes_through_return_values(sink):
    wrapped = guard(lambda x: x * 2, widget="W", event="e")
    assert wrapped(21) == 42
    assert sink == []


def test_event_handler_is_guarded_end_to_end(qapp, sink):
    class Button(LimeObject, QPushButton):
        onClick = Event("clicked", passes_self=True)

    b = Button()
    b.setOnClick(lambda widget: 1 / 0)
    b.click()                                    # must not raise
    assert len(sink) == 1


def test_handler_receives_the_widget_when_passes_self(qapp, sink):
    class Button(LimeObject, QPushButton):
        onClick = Event("clicked", passes_self=True)

    seen = []
    b = Button()
    b.setOnClick(seen.append)
    b.click()
    assert seen == [b]


def test_replacing_a_handler_disconnects_the_previous_one(qapp, sink):
    class Button(LimeObject, QPushButton):
        onClick = Event("clicked", passes_self=False)

    calls = []
    b = Button()
    b.setOnClick(lambda: calls.append("first"))
    b.setOnClick(lambda: calls.append("second"))
    b.click()
    assert calls == ["second"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/kernel/test_guard.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'limekit.kernel.bridge'`

- [ ] **Step 3: Write minimal implementation**

```python
# limekit/kernel/bridge/__init__.py
```

```python
# limekit/kernel/bridge/guard.py
"""The single seam every Lua callback crosses on its way into Python.

Nothing attached through the generated accessors can leak an exception into
the Qt event loop.
"""

import traceback

from limekit.kernel.errors import WidgetCallbackError

_DEFAULT_SINK = None


def _print_sink(error):
    print(f"\n{error}")
    traceback.print_exception(type(error), error, error.__traceback__)


_sink = _print_sink


def set_error_sink(fn):
    """Route guarded errors somewhere (the app's handler, or a test list)."""
    global _sink
    _sink = fn


def reset_error_sink():
    global _sink
    _sink = _print_sink


def guard(fn, *, widget, event):
    """Wrap a callable so it reports rather than raises."""

    def guarded(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:                       # noqa: BLE001
            error = WidgetCallbackError(str(exc), widget=widget, event=event)
            error.__cause__ = exc
            _sink(error)
            return None

    guarded.__name__ = f"guarded_{event}"
    return guarded
```

Add to `limekit/kernel/declarative.py`:

```python
from limekit.kernel.bridge.guard import guard
```

```python
def _install_event(cls, event):
    """Generate `setOn<Name>` for one Event.

    The generated setter is the only way to attach a handler, so every
    handler is guarded by construction.
    """
    setter_name = event.setter_name()
    signal_name, passes_self, label = event.qt_signal, event.passes_self, event.name
    slot_attr = f"_lime_slot_{event.name}"

    def attach(self, handler, _sig=signal_name, _self=passes_self,
               _ev=label, _slot=slot_attr):
        signal = getattr(self, _sig)

        previous = getattr(self, _slot, None)
        if previous is not None:
            signal.disconnect(previous)

        widget_name = type(self).__name__
        if _self:
            def call(*args, _h=handler, _w=self):
                return _h(_w, *args)
        else:
            def call(*args, _h=handler):
                return _h(*args)

        slot = guard(call, widget=widget_name, event=_ev)
        setattr(self, _slot, slot)
        signal.connect(slot)
        return self

    attach.__name__ = setter_name
    attach.__doc__ = event.doc or None
    setattr(cls, setter_name, attach)
```

And in `__init_subclass__`, after the prop loop:

```python
        for event in cls.__events__:
            _install_event(cls, event)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/kernel/ -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add limekit/kernel/bridge/ limekit/kernel/declarative.py tests/kernel/test_guard.py
git commit -m "feat(kernel): guard every Lua callback at a single seam"
```

---

### Task 8: Registry

**Files:**
- Create: `limekit/kernel/registry.py`
- Modify: `limekit/kernel/declarative.py`
- Create: `tests/kernel/test_registry.py`

**Interfaces:**
- Consumes: `RegistryError`, `LimeObject`
- Produces: `Registry` with `.register(cls)`, `.get(path)`, `.modules()` → `dict[str, dict[str, type]]`, `.all()` → `tuple[type, ...]`, `.clear()`; module-level singleton `registry`

- [ ] **Step 1: Write the failing test**

```python
# tests/kernel/test_registry.py
import pytest
from PySide6.QtWidgets import QPushButton
from limekit.kernel.registry import Registry, registry
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import RegistryError


def test_register_and_get(qapp):
    r = Registry()

    class W(LimeObject, QPushButton):
        pass

    r.register("ui.Thing", W)
    assert r.get("ui.Thing") is W


def test_unknown_path_raises(qapp):
    with pytest.raises(RegistryError, match="ui.Missing"):
        Registry().get("ui.Missing")


def test_duplicate_path_raises(qapp):
    r = Registry()

    class A(LimeObject, QPushButton):
        pass

    class B(LimeObject, QPushButton):
        pass

    r.register("ui.Thing", A)
    with pytest.raises(RegistryError, match="already registered"):
        r.register("ui.Thing", B)


def test_path_must_be_dotted(qapp):
    class W(LimeObject, QPushButton):
        pass

    with pytest.raises(RegistryError, match="module.Name"):
        Registry().register("Thing", W)


def test_modules_groups_by_prefix(qapp):
    r = Registry()

    class A(LimeObject, QPushButton):
        pass

    class B(LimeObject, QPushButton):
        pass

    r.register("ui.Button", A)
    r.register("fs.Reader", B)
    assert r.modules() == {"ui": {"Button": A}, "fs": {"Reader": B}}


def test_declaring_lime_auto_registers(qapp):
    class W(LimeObject, QPushButton):
        __lime__ = "ui.AutoRegistered"

    assert registry.get("ui.AutoRegistered") is W
    registry.clear_path("ui.AutoRegistered")


def test_classes_without_lime_are_not_registered(qapp):
    class W(LimeObject, QPushButton):
        pass

    assert W not in registry.all()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/kernel/test_registry.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'limekit.kernel.registry'`

- [ ] **Step 3: Write minimal implementation**

```python
# limekit/kernel/registry.py
"""The single source of truth: dotted path -> class.

Generators for limekit.lua, the LSP stubs and manifest.py all walk this.
"""

from limekit.kernel.errors import RegistryError


class Registry:
    def __init__(self):
        self._by_path = {}

    def register(self, path, cls):
        if "." not in path:
            raise RegistryError(
                f"{path!r} is not a dotted path; expected 'module.Name'"
            )
        existing = self._by_path.get(path)
        if existing is not None and existing is not cls:
            raise RegistryError(
                f"{path!r} is already registered to {existing.__name__}"
            )
        self._by_path[path] = cls

    def get(self, path):
        try:
            return self._by_path[path]
        except KeyError:
            raise RegistryError(f"nothing registered at {path!r}") from None

    def modules(self):
        """Group registrations by their module prefix, for Lua's require()."""
        grouped = {}
        for path, cls in self._by_path.items():
            module, _, name = path.rpartition(".")
            grouped.setdefault(module, {})[name] = cls
        return grouped

    def paths(self):
        return tuple(sorted(self._by_path))

    def all(self):
        return tuple(self._by_path.values())

    def clear(self):
        self._by_path.clear()

    def clear_path(self, path):
        self._by_path.pop(path, None)


registry = Registry()
```

In `limekit/kernel/declarative.py`, import the singleton and auto-register at the end of `__init_subclass__`:

```python
from limekit.kernel.registry import registry
```

```python
        # `__lime__` declared directly on this class is the registration.
        # `vars(cls)` rather than `cls.__lime__` so subclasses do not
        # re-register under their parent's path.
        path = vars(cls).get("__lime__")
        if path:
            registry.register(path, cls)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/kernel/ -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add limekit/kernel/registry.py limekit/kernel/declarative.py tests/kernel/test_registry.py
git commit -m "feat(kernel): add registry with auto-registration via __lime__"
```

---

### Task 9: Bridge conversions

`ComboBox.setItems` guards with `lupa.lua_type(items) == "table"`; `ListBox.setItems` calls `.values()` unconditionally and crashes on a Python list. `as_sequence` removes that whole bug class.

**Files:**
- Create: `limekit/kernel/bridge/convert.py`
- Create: `tests/kernel/test_convert.py`

**Interfaces:**
- Consumes: `BridgeError`
- Produces: `set_runtime(lua)`, `to_lua(v)`, `to_py(v)`, `as_sequence(v)` → `list`, `as_mapping(v)` → `dict`, `as_callable(v)`

- [ ] **Step 1: Write the failing test**

```python
# tests/kernel/test_convert.py
import pytest
from lupa import LuaRuntime
from limekit.kernel.bridge import convert
from limekit.kernel.errors import BridgeError


@pytest.fixture
def lua():
    runtime = LuaRuntime(unpack_returned_tuples=True)
    convert.set_runtime(runtime)
    yield runtime
    convert.set_runtime(None)


def test_as_sequence_accepts_a_lua_table(lua):
    table = lua.eval('{"a", "b", "c"}')
    assert convert.as_sequence(table) == ["a", "b", "c"]


def test_as_sequence_accepts_a_python_list(lua):
    """ListBox.setItems crashed on this; ComboBox.setItems did not."""
    assert convert.as_sequence(["a", "b"]) == ["a", "b"]


def test_as_sequence_accepts_a_tuple_and_generator(lua):
    assert convert.as_sequence(("a", "b")) == ["a", "b"]
    assert convert.as_sequence(i for i in range(3)) == [0, 1, 2]


def test_as_sequence_treats_a_string_as_one_item(lua):
    assert convert.as_sequence("abc") == ["abc"]


def test_as_sequence_of_none_is_empty(lua):
    assert convert.as_sequence(None) == []


def test_as_mapping_from_lua_table(lua):
    table = lua.eval('{x = 1, y = 2}')
    assert convert.as_mapping(table) == {"x": 1, "y": 2}


def test_to_py_detects_array_vs_map(lua):
    assert convert.to_py(lua.eval('{"a", "b"}')) == ["a", "b"]
    assert convert.to_py(lua.eval('{x = 1}')) == {"x": 1}


def test_to_py_is_recursive(lua):
    assert convert.to_py(lua.eval('{a = {1, 2}}')) == {"a": [1, 2]}


def test_to_lua_round_trips(lua):
    assert convert.to_py(convert.to_lua(["a", "b"])) == ["a", "b"]
    assert convert.to_py(convert.to_lua({"x": 1})) == {"x": 1}


def test_to_lua_without_a_runtime_raises():
    convert.set_runtime(None)
    with pytest.raises(BridgeError, match="runtime"):
        convert.to_lua([1, 2])


def test_as_callable_accepts_a_lua_function(lua):
    fn = lua.eval('function(x) return x + 1 end')
    assert convert.as_callable(fn)(1) == 2


def test_as_callable_rejects_a_non_callable(lua):
    with pytest.raises(BridgeError, match="callable"):
        convert.as_callable(42)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/kernel/test_convert.py -v`
Expected: FAIL with `ImportError: cannot import name 'convert'`

- [ ] **Step 3: Write minimal implementation**

```python
# limekit/kernel/bridge/convert.py
"""Every Lua <-> Python crossing goes through here.

Previously each widget converted its own arguments, which is how ComboBox
and ListBox ended up disagreeing about whether a Python list was acceptable.
"""

import lupa

from limekit.kernel.errors import BridgeError

_runtime = None


def set_runtime(lua):
    """Called by LimeRuntime once the LuaRuntime exists."""
    global _runtime
    _runtime = lua


def _is_lua_table(value):
    return lupa.lua_type(value) == "table"


def to_lua(value):
    """Python -> Lua. Sequences become 1-indexed tables."""
    if _runtime is None:
        raise BridgeError("no Lua runtime is bound; call set_runtime() first")
    if isinstance(value, dict):
        return _runtime.table_from({k: to_lua(v) for k, v in value.items()})
    if isinstance(value, (list, tuple, set)):
        return _runtime.table_from([to_lua(v) for v in value])
    return value


def to_py(value):
    """Lua -> Python. A table with keys 1..n becomes a list, else a dict."""
    if not _is_lua_table(value):
        return value

    items = dict(value.items())
    keys = list(items)
    if keys and all(isinstance(k, int) for k in keys) and \
            sorted(keys) == list(range(1, len(keys) + 1)):
        return [to_py(items[k]) for k in sorted(keys)]
    return {k: to_py(v) for k, v in items.items()}


def as_sequence(value):
    """Accept a Lua table OR any Python sequence; always return a list.

    A string counts as a single item, not a sequence of characters.
    """
    if value is None:
        return []
    if _is_lua_table(value):
        result = to_py(value)
        return result if isinstance(result, list) else list(result.values())
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple, set)):
        return list(value)
    try:
        return list(value)
    except TypeError:
        return [value]


def as_mapping(value):
    if value is None:
        return {}
    if _is_lua_table(value):
        result = to_py(value)
        if isinstance(result, dict):
            return result
        return dict(enumerate(result, start=1))
    if isinstance(value, dict):
        return dict(value)
    raise BridgeError(f"expected a table or mapping, got {type(value).__name__}")


def as_callable(value):
    if not callable(value):
        raise BridgeError(f"expected a callable, got {type(value).__name__}")
    return value
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/kernel/test_convert.py -v`
Expected: PASS (12 tests)

- [ ] **Step 5: Commit**

```bash
git add limekit/kernel/bridge/convert.py tests/kernel/test_convert.py
git commit -m "feat(kernel): centralise Lua/Python conversion"
```

---

### Task 10: Lua runtime and namespaced modules

Replaces ~138 flat globals with `require("limekit.ui")`. Chunk naming makes tracebacks report the real `.lua` file, deleting the `error_str.rfind('>"]')` string-surgery duplicated in `runner.py` and `error_handler.py`.

**Files:**
- Create: `limekit/kernel/bridge/runtime.py`
- Create: `tests/kernel/test_runtime.py`

**Interfaces:**
- Consumes: `Registry`, `convert.set_runtime`, `LuaError`
- Produces: `LimeRuntime(registry)` with `.lua`, `.install_modules()`, `.execute(source, chunkname)`, `.eval(source, chunkname)`, `.globals()`

- [ ] **Step 1: Write the failing test**

```python
# tests/kernel/test_runtime.py
import pytest
from PySide6.QtWidgets import QPushButton
from limekit.kernel.bridge.runtime import LimeRuntime
from limekit.kernel.registry import Registry
from limekit.kernel.declarative import LimeObject
from limekit.kernel.spec import Prop
from limekit.kernel.errors import LuaError


@pytest.fixture
def rt(qapp):
    class Button(LimeObject, QPushButton):
        text = Prop(str, default="Button", qt=("text", "setText"), coerce=str)

        def __init__(self, text="Button"):
            super().__init__()
            self.setText(text)

    reg = Registry()
    reg.register("ui.Button", Button)
    runtime = LimeRuntime(reg)
    runtime.install_modules()
    return runtime


def test_modules_are_requirable(rt):
    result = rt.eval(
        'local ui = require("limekit.ui") '
        'return ui.Button("hi"):getText()'
    )
    assert result == "hi"


def test_no_flat_globals_leak(rt):
    for name in ("Button", "eval", "str", "int", "dict", "tuple", "print", "len"):
        assert rt.eval(f'return {name} == nil'), f"{name} leaked into globals"


def test_unknown_module_raises(rt):
    with pytest.raises(LuaError):
        rt.execute('require("limekit.nope")')


def test_syntax_error_reports_the_real_file(rt):
    with pytest.raises(LuaError) as exc:
        rt.execute("this is not lua", chunkname="scripts/main.lua")
    assert exc.value.source == "scripts/main.lua"


def test_runtime_error_reports_the_real_line(rt):
    source = "local x = 1\nerror('boom')\n"
    with pytest.raises(LuaError) as exc:
        rt.execute(source, chunkname="scripts/main.lua")
    assert exc.value.source == "scripts/main.lua"
    assert exc.value.line == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/kernel/test_runtime.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'limekit.kernel.bridge.runtime'`

- [ ] **Step 3: Write minimal implementation**

```python
# limekit/kernel/bridge/runtime.py
"""Owns the LuaRuntime and exposes the registry as requirable modules."""

import re

import lupa
from lupa import LuaRuntime

from limekit.kernel.bridge import convert
from limekit.kernel.errors import LuaError

# Lua reports errors as [string "name"]:LINE: message
_LOCATION = re.compile(r'^\[string "(?P<source>[^"]*)"\]:(?P<line>\d+):\s*(?P<msg>.*)',
                       re.DOTALL)


class LimeRuntime:
    """The Lua side of the bridge."""

    def __init__(self, registry, *, package="limekit"):
        self.registry = registry
        self.package = package
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        convert.set_runtime(self.lua)

    def globals(self):
        return self.lua.globals()

    def install_modules(self):
        """Expose every registered class through package.preload.

        Lua then reaches them with `require("limekit.ui")`, so nothing is
        installed as a bare global.
        """
        preload = self.lua.eval("package.preload")
        for module, members in self.registry.modules().items():
            table = self.lua.table_from(dict(members))
            preload[f"{self.package}.{module}"] = (
                lambda _name=None, _t=table: _t
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
        both runner.py and error_handler.py.
        """
        text = str(exc)
        match = _LOCATION.match(text)
        if match:
            return LuaError(
                match.group("msg").strip(),
                source=match.group("source") or chunkname,
                line=int(match.group("line")),
            )
        return LuaError(text, source=chunkname)
```

> **Note for the implementer:** lupa's `execute`/`eval` accept the chunk name as
> the `name=` keyword. If the installed lupa build rejects it, fall back to
> `self.lua.compile(source, name=chunkname)()` — verify with
> `python -c "import lupa,inspect; print(inspect.signature(lupa.LuaRuntime().execute))"`
> before assuming either form.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/kernel/test_runtime.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add limekit/kernel/bridge/runtime.py tests/kernel/test_runtime.py
git commit -m "feat(kernel): namespaced Lua modules and source-mapped errors"
```

---

### Task 11: Application lifecycle

`App.app = QApplication(sys.argv)` currently runs at class-definition time and `runner.py` runs the app at import, so `import limekit` launches Qt. That is why there are no tests.

**Files:**
- Create: `limekit/kernel/app.py`
- Create: `limekit/__main__.py`
- Create: `tests/kernel/test_app.py`

**Interfaces:**
- Consumes: `LimeRuntime`, `registry`, `set_error_sink`, `ProjectError`
- Produces: `LimekitApp(project_path, *, argv=None, frozen=False)` with `.boot()`, `.load_project()`, `.run()` → int, `.shutdown()`, context-manager support, and `.runtime`

- [ ] **Step 1: Write the failing test**

```python
# tests/kernel/test_app.py
import pytest
from limekit.kernel.app import LimekitApp
from limekit.kernel.errors import ProjectError


@pytest.fixture
def project(tmp_path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "main.lua").write_text(
        'local ui = require("limekit.ui")\nRAN = true\n', encoding="utf-8"
    )
    (tmp_path / "app.json").write_text('{"project": {"name": "T"}}', encoding="utf-8")
    return tmp_path


def test_importing_limekit_has_no_side_effects():
    """A fresh interpreter must not construct a QApplication on import."""
    import subprocess, sys
    code = (
        "import limekit, limekit.kernel.app;"
        "from PySide6.QtWidgets import QApplication;"
        "print(QApplication.instance() is None)"
    )
    out = subprocess.run([sys.executable, "-c", code],
                         capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "True"


def test_boot_creates_a_runtime(project):
    app = LimekitApp(project)
    app.boot()
    assert app.runtime is not None
    app.shutdown()


def test_load_project_executes_main_lua(project):
    app = LimekitApp(project)
    app.boot()
    app.load_project()
    assert app.runtime.eval("return RAN") is True
    app.shutdown()


def test_missing_main_lua_raises_project_error(tmp_path):
    (tmp_path / "scripts").mkdir()
    app = LimekitApp(tmp_path)
    app.boot()
    with pytest.raises(ProjectError, match="main.lua"):
        app.load_project()
    app.shutdown()


def test_context_manager_shuts_down(project):
    with LimekitApp(project) as app:
        app.load_project()
        assert app.runtime is not None
    assert app.runtime is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/kernel/test_app.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'limekit.kernel.app'`

- [ ] **Step 3: Write minimal implementation**

```python
# limekit/kernel/app.py
"""Explicit application lifecycle.

Nothing here runs at import time: constructing a LimekitApp is what creates
the QApplication, so the framework can be imported by tests and tooling.
"""

import sys
from pathlib import Path

from limekit.kernel.bridge.guard import set_error_sink
from limekit.kernel.bridge.runtime import LimeRuntime
from limekit.kernel.errors import ProjectError
from limekit.kernel.registry import registry


class LimekitApp:
    def __init__(self, project_path, *, argv=None, frozen=False):
        self.project_path = Path(project_path)
        self.argv = list(argv) if argv is not None else []
        self.frozen = frozen
        self.qt_app = None
        self.runtime = None
        self._errors = []

    # -- lifecycle ---------------------------------------------------------

    def boot(self):
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QApplication

        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        self.qt_app = QApplication.instance() or QApplication(self.argv)

        from limekit.kernel import manifest
        manifest.import_all()

        self.runtime = LimeRuntime(registry)
        self.runtime.install_modules()
        set_error_sink(self._on_error)
        return self

    def load_project(self):
        main = self.project_path / "scripts" / "main.lua"
        if not main.is_file():
            raise ProjectError(f"no main.lua found at {main}")

        self._set_lua_path()
        relative = main.relative_to(self.project_path).as_posix()
        self.runtime.execute(main.read_text(encoding="utf-8"), chunkname=relative)
        return self

    def run(self):
        if self.qt_app is None:
            raise ProjectError("boot() must be called before run()")
        return self.qt_app.exec()

    def shutdown(self):
        self.runtime = None
        self.qt_app = None

    # -- internals ---------------------------------------------------------

    def _set_lua_path(self):
        roots = [self.project_path / "scripts", self.project_path / "misc"]
        entries = []
        for root in roots:
            if not root.is_dir():
                continue
            for directory in [root, *(p for p in root.rglob("*") if p.is_dir())]:
                posix = directory.as_posix()
                entries.append(f"{posix}/?.lua")
                entries.append(f"{posix}/?/init.lua")
        if entries:
            joined = ";".join(dict.fromkeys(entries)) + ";"
            self.runtime.execute(
                f"package.path = {joined!r} .. package.path",
                chunkname="<limekit:package.path>",
            )

    def _on_error(self, error):
        self._errors.append(error)
        print(f"\n{error}", file=sys.stderr)

    @property
    def errors(self):
        return tuple(self._errors)

    # -- context manager ---------------------------------------------------

    def __enter__(self):
        return self.boot()

    def __exit__(self, *exc_info):
        self.shutdown()
        return False
```

```python
# limekit/__main__.py
"""Console entry point. The only place sys.exit is called."""

import sys

from limekit.kernel.app import LimekitApp


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("usage: python -m limekit <project-path>", file=sys.stderr)
        return 2

    app = LimekitApp(argv[0], argv=argv)
    app.boot()
    app.load_project()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/kernel/test_app.py -v`
Expected: PASS (5 tests). Task 12 creates `manifest.py`; until then add a temporary
`limekit/kernel/manifest.py` containing `MODULES = ()` and
`def import_all(): pass` so `boot()` resolves.

- [ ] **Step 5: Commit**

```bash
git add limekit/kernel/app.py limekit/__main__.py limekit/kernel/manifest.py tests/kernel/test_app.py
git commit -m "feat(kernel): explicit LimekitApp lifecycle with no import side effects"
```

---

### Task 12: Manifest generator

Closes the dev/frozen divergence. Today development walks the filesystem while frozen mode uses a hand-maintained 130-entry list at `app_engine.py:399-531`; forgetting an entry ships a broken `.exe`.

**Files:**
- Create: `tools/generate_manifest.py`
- Modify: `limekit/kernel/manifest.py` (generated)
- Create: `tests/kernel/test_manifest.py`

**Interfaces:**
- Consumes: `registry`
- Produces: `manifest.MODULES` (tuple of dotted module names), `manifest.import_all()`; `tools/generate_manifest.py` with `discover(package_root)` → `tuple[str, ...]` and `render(modules)` → str

- [ ] **Step 1: Write the failing test**

```python
# tests/kernel/test_manifest.py
import subprocess
import sys
from pathlib import Path

from limekit.kernel import manifest

REPO = Path(__file__).resolve().parents[2]


def test_manifest_is_non_empty():
    assert len(manifest.MODULES) > 0


def test_every_listed_module_is_importable():
    import importlib
    for name in manifest.MODULES:
        importlib.import_module(name)


def test_import_all_populates_the_registry():
    from limekit.kernel.registry import registry
    manifest.import_all()
    registered = {cls.__lime__ for cls in registry.all()}
    assert registered, "import_all() registered nothing"
    # Every listed module must contribute at least one registered class.
    assert len(registered) >= len(manifest.MODULES)


def test_regenerating_the_manifest_is_a_no_op():
    """The check that would have caught the frozen-mode divergence."""
    current = (REPO / "limekit" / "kernel" / "manifest.py").read_text(encoding="utf-8")
    regenerated = subprocess.run(
        [sys.executable, str(REPO / "tools" / "generate_manifest.py"), "--stdout"],
        capture_output=True, text=True, check=True, cwd=REPO,
    ).stdout
    assert current.replace("\r\n", "\n") == regenerated.replace("\r\n", "\n"), (
        "manifest.py is stale - run: python tools/generate_manifest.py"
    )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/kernel/test_manifest.py -v`
Expected: FAIL — `MODULES` is the empty placeholder from Task 11 and `tools/generate_manifest.py` does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
# tools/generate_manifest.py
"""Emit limekit/kernel/manifest.py from the classes that declare __lime__.

Run after adding or removing any exported class:

    python tools/generate_manifest.py
"""

import argparse
import ast
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PACKAGE = REPO / "limekit"
SKIP = {"kernel", "build", "__pycache__"}

HEADER = '''"""Explicit import list for every class exposed to Lua.

GENERATED by tools/generate_manifest.py - do not edit by hand.

Development and frozen builds both import from this list, so a class that is
missing here is missing in BOTH, rather than only in the packaged app.
"""

import importlib

MODULES = (
'''

FOOTER = ''')


def import_all():
    """Import every module so their __lime__ declarations register."""
    for name in MODULES:
        importlib.import_module(name)
'''


def declares_lime(path):
    """True if the file assigns __lime__ at class scope."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return False
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for stmt in node.body:
            targets = (
                stmt.targets if isinstance(stmt, ast.Assign)
                else [stmt.target] if isinstance(stmt, ast.AnnAssign)
                else []
            )
            for target in targets:
                if isinstance(target, ast.Name) and target.id == "__lime__":
                    return True
    return False


def discover(package_root=PACKAGE):
    modules = []
    for path in sorted(package_root.rglob("*.py")):
        if set(path.relative_to(package_root).parts) & SKIP:
            continue
        if path.name == "__init__.py":
            continue
        if declares_lime(path):
            rel = path.relative_to(package_root.parent).with_suffix("")
            modules.append(".".join(rel.parts))
    return tuple(modules)


def render(modules):
    body = "".join(f'    "{name}",\n' for name in modules)
    return HEADER + body + FOOTER


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stdout", action="store_true",
                        help="print instead of writing the file")
    args = parser.parse_args()

    text = render(discover())
    if args.stdout:
        sys.stdout.write(text)
    else:
        target = PACKAGE / "kernel" / "manifest.py"
        target.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {target}")


if __name__ == "__main__":
    main()
```

Then generate it:

```bash
python tools/generate_manifest.py
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/kernel/test_manifest.py -v`
Expected: PASS (4 tests). Task 16 runs before this one (see Execution Order), so the
registry already contains the five pilot widgets and `MODULES` is non-empty.

- [ ] **Step 5: Commit**

```bash
git add tools/generate_manifest.py limekit/kernel/manifest.py tests/kernel/test_manifest.py
git commit -m "feat(kernel): generate the module manifest from __lime__ declarations"
```

---

### Task 13: Lua binding generator

Replaces the hand-written 340-line `limekit.lua` (95 functions) and deletes `limekit/lua/script.py`, which is a byte-identical duplicate of it.

**Files:**
- Create: `tools/generate_lua.py`
- Create: `limekit/runtime/lua/limekit.lua` (generated)
- Delete: `limekit/lua/script.py`
- Create: `tests/kernel/test_generate_lua.py`

**Interfaces:**
- Consumes: `registry`, `manifest.import_all`
- Produces: `tools/generate_lua.py` with `render(registry)` → str

- [ ] **Step 1: Write the failing test**

```python
# tests/kernel/test_generate_lua.py
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GENERATED = REPO / "limekit" / "runtime" / "lua" / "limekit.lua"


def test_generated_lua_exists():
    assert GENERATED.is_file()


def test_generated_lua_declares_every_module():
    from limekit.kernel import manifest
    from limekit.kernel.registry import registry
    manifest.import_all()

    text = GENERATED.read_text(encoding="utf-8")
    for module in registry.modules():
        assert f'limekit.{module}' in text


def test_dead_duplicate_is_gone():
    """lua/script.py held a byte-identical copy of limekit.lua."""
    assert not (REPO / "limekit" / "lua" / "script.py").exists()


def test_regenerating_is_a_no_op():
    current = GENERATED.read_text(encoding="utf-8")
    regenerated = subprocess.run(
        [sys.executable, str(REPO / "tools" / "generate_lua.py"), "--stdout"],
        capture_output=True, text=True, check=True, cwd=REPO,
    ).stdout
    assert current.replace("\r\n", "\n") == regenerated.replace("\r\n", "\n"), (
        "limekit.lua is stale - run: python tools/generate_lua.py"
    )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/kernel/test_generate_lua.py -v`
Expected: FAIL — neither the generator nor the generated file exists, and `lua/script.py` is still present.

- [ ] **Step 3: Write minimal implementation**

```python
# tools/generate_lua.py
"""Emit limekit/runtime/lua/limekit.lua from the registry.

Replaces the hand-maintained app table, which had to be kept in sync with
Python by hand in two separate files.

    python tools/generate_lua.py
"""

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from limekit.kernel import manifest                      # noqa: E402
from limekit.kernel.registry import registry             # noqa: E402

HEADER = """-- GENERATED by tools/generate_lua.py - do not edit by hand.
--
-- Every class carrying a __lime__ path is reachable here. Require the module
-- you need rather than relying on globals:
--
--     local ui = require("limekit.ui")
--     local win = ui.Window { title = "Hello" }

local limekit = {}

"""

FOOTER = """
return limekit
"""


def render():
    manifest.import_all()
    lines = [HEADER]
    for module, members in sorted(registry.modules().items()):
        lines.append(f'-- {module}\n')
        lines.append(f'limekit.{module} = require("limekit.{module}")\n')
        for name in sorted(members):
            lines.append(f'--   {module}.{name}\n')
        lines.append("\n")
    lines.append(FOOTER)
    return "".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()

    text = render()
    if args.stdout:
        sys.stdout.write(text)
    else:
        target = REPO / "limekit" / "runtime" / "lua" / "limekit.lua"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {target}")


if __name__ == "__main__":
    main()
```

```bash
python tools/generate_lua.py
git rm limekit/lua/script.py
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/kernel/test_generate_lua.py -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add tools/generate_lua.py limekit/runtime/lua/limekit.lua tests/kernel/test_generate_lua.py
git rm --cached limekit/lua/script.py 2>/dev/null || true
git commit -m "feat(kernel): generate limekit.lua and delete its dead duplicate"
```

---

### Task 14: LSP stub generator

New capability. Lua users currently have no autocomplete or type information.

**Files:**
- Create: `tools/generate_stubs.py`
- Create: `limekit/runtime/lua/stubs/` (generated)
- Create: `tests/kernel/test_generate_stubs.py`

**Interfaces:**
- Consumes: `registry`, `Prop.accessor_names()`, `Event.setter_name()`
- Produces: one `<module>.lua` stub per registry module, in LuaLS annotation format

- [ ] **Step 1: Write the failing test**

```python
# tests/kernel/test_generate_stubs.py
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STUBS = REPO / "limekit" / "runtime" / "lua" / "stubs"


def test_a_stub_exists_per_module():
    from limekit.kernel import manifest
    from limekit.kernel.registry import registry
    manifest.import_all()
    for module in registry.modules():
        assert (STUBS / f"{module}.lua").is_file()


def test_stub_documents_generated_accessors():
    from limekit.kernel import manifest
    from limekit.kernel.registry import registry
    manifest.import_all()

    cls = registry.get("ui.Button")     # Task 16 runs first; this must exist
    text = (STUBS / "ui.lua").read_text(encoding="utf-8")
    for prop in cls.__props__:
        getter, setter, _ = prop.accessor_names()
        assert getter in text
        assert setter in text


def test_regenerating_is_a_no_op():
    before = {p.name: p.read_text(encoding="utf-8") for p in STUBS.glob("*.lua")}
    subprocess.run(
        [sys.executable, str(REPO / "tools" / "generate_stubs.py")],
        capture_output=True, text=True, check=True, cwd=REPO,
    )
    after = {p.name: p.read_text(encoding="utf-8") for p in STUBS.glob("*.lua")}
    assert before == after, "stubs are stale - run: python tools/generate_stubs.py"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/kernel/test_generate_stubs.py -v`
Expected: FAIL — the stubs directory does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
# tools/generate_stubs.py
"""Emit Lua Language Server stubs so Lua users get autocomplete.

    python tools/generate_stubs.py
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from limekit.kernel import manifest                      # noqa: E402
from limekit.kernel.registry import registry             # noqa: E402

LUA_TYPES = {
    str: "string", int: "integer", float: "number", bool: "boolean",
}


def lua_type(python_type):
    return LUA_TYPES.get(python_type, "any")


def render_class(name, cls):
    lines = [f"---@class {name}"]
    lines.append(f"local {name} = {{}}")
    lines.append("")

    for prop in cls.__props__:
        getter, setter, alias = prop.accessor_names()
        typename = lua_type(prop.type)
        doc = prop.doc or f"the {prop.name} property"

        lines.append(f"--- Get {doc}.")
        lines.append(f"---@return {typename}")
        lines.append(f"function {name}:{getter}() end")
        lines.append("")

        lines.append(f"--- Set {doc}.")
        lines.append(f"---@param value {typename}")
        lines.append(f"---@return {name}")
        lines.append(f"function {name}:{setter}(value) end")
        lines.append("")

        if alias:
            lines.append(f"--- Get {doc}.")
            lines.append("---@return boolean")
            lines.append(f"function {name}:{alias}() end")
            lines.append("")

    for event in cls.__events__:
        doc = event.doc or f"Attach a handler for {event.name}."
        lines.append(f"--- {doc}")
        lines.append(f"---@param handler fun(widget: {name})")
        lines.append(f"---@return {name}")
        lines.append(f"function {name}:{event.setter_name()}(handler) end")
        lines.append("")

    return "\n".join(lines)


def render_module(module, members):
    lines = [
        "---@meta",
        "-- GENERATED by tools/generate_stubs.py - do not edit by hand.",
        "",
    ]
    for name, cls in sorted(members.items()):
        lines.append(render_class(name, cls))
    lines.append(f"local {module} = {{}}")
    for name in sorted(members):
        lines.append(f"{module}.{name} = {name}")
    lines.append(f"return {module}")
    lines.append("")
    return "\n".join(lines)


def main():
    manifest.import_all()
    target = REPO / "limekit" / "runtime" / "lua" / "stubs"
    target.mkdir(parents=True, exist_ok=True)

    for module, members in registry.modules().items():
        path = target / f"{module}.lua"
        path.write_text(render_module(module, members), encoding="utf-8", newline="\n")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
```

```bash
python tools/generate_stubs.py
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/kernel/test_generate_stubs.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add tools/generate_stubs.py limekit/runtime/lua/stubs/ tests/kernel/test_generate_stubs.py
git commit -m "feat(kernel): generate Lua LSP stubs from the registry"
```

---

### Task 15: Layering enforcement

Makes the dependency rule a test rather than a convention, so `GlobalEngine` cannot grow back.

**Files:**
- Create: `.importlinter`
- Create: `tests/test_layering.py`

**Interfaces:**
- Consumes: nothing
- Produces: a CI-enforced guarantee that `kernel` imports nothing from `widgets`, `services` or `toolkit`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_layering.py
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_import_contracts_hold():
    result = subprocess.run(
        [sys.executable, "-m", "importlinter.cli", "lint"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_kernel_does_not_import_the_legacy_engine():
    """The new kernel must not reach back into the 1.x runtime.

    The legacy tree itself survives P0 so existing apps keep working; it is
    removed in P1. What matters here is that kernel/ never depends on it.
    """
    offenders = []
    for path in (REPO / "limekit" / "kernel").rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "limekit.engine" in text or "GlobalEngine" in text:
            offenders.append(path.relative_to(REPO).as_posix())
    assert offenders == [], f"kernel reaches into the legacy engine: {offenders}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_layering.py -v`
Expected: FAIL — `.importlinter` does not exist, and `GlobalEngine` is still referenced by the legacy engine.

- [ ] **Step 3: Write minimal implementation**

```ini
# .importlinter
[importlinter]
root_package = limekit

[importlinter:contract:kernel-is-independent]
name = kernel imports nothing from the rest of limekit
type = forbidden
source_modules =
    limekit.kernel
forbidden_modules =
    limekit.widgets
    limekit.build
    limekit.engine
    limekit.components
    limekit.utils
    limekit.gui
    limekit.core

[importlinter:contract:layers]
name = strict layering
type = layers
layers =
    limekit.widgets
    limekit.kernel
```

> **Scope note.** The legacy `limekit/engine/`, `limekit/components/`, `limekit/utils/`
> and `limekit/gui/` trees survive P0 untouched, so existing 1.x apps keep running
> while the new kernel is built beside them. `GlobalEngine` therefore still exists;
> it has 8 references in `app_engine.py` and `converters.py`. Removing it is **P1
> work**, done when those trees are retired. What P0 guarantees, and what this
> contract enforces, is that `limekit/kernel/` never depends on any of them —
> so the layering violation cannot propagate into the new code.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_layering.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add .importlinter tests/test_layering.py
git commit -m "test: enforce kernel independence from the legacy trees"
```

---

### Task 16: Pilot widget migration

Proves the kernel end-to-end on the five widgets whose current implementations demonstrate the divergence problems: `Button` (the only guarded one), `Label` (duplicate cursor keys), `CheckBox` (no `str()` coercion), `ListBox` and `ComboBox` (incompatible `setItems`).

**Files:**
- Create: `limekit/widgets/__init__.py`
- Create: `limekit/widgets/base.py`
- Create: `limekit/widgets/button.py`
- Create: `limekit/widgets/label.py`
- Create: `limekit/widgets/checkbox.py`
- Create: `limekit/widgets/listbox.py`
- Create: `limekit/widgets/combobox.py`
- Create: `tests/widgets/test_pilot_widgets.py`

**Interfaces:**
- Consumes: `LimeObject`, `Prop`, `Event`, coercions, `as_sequence`
- Produces: `LimeWidget` (shared sizing/styling props) and five migrated widgets registered at `ui.Button`, `ui.Label`, `ui.CheckBox`, `ui.ListBox`, `ui.ComboBox`

- [ ] **Step 1: Write the failing test**

```python
# tests/widgets/test_pilot_widgets.py
import pytest
from limekit.kernel.bridge.guard import set_error_sink, reset_error_sink


@pytest.fixture(autouse=True)
def sink():
    captured = []
    set_error_sink(captured.append)
    yield captured
    reset_error_sink()


def test_button_text_round_trips(qapp):
    from limekit.widgets.button import Button
    assert Button("hi").getText() == "hi"


def test_checkbox_coerces_like_button(qapp):
    """CheckBox.setText used to skip the str() that Button applied."""
    from limekit.widgets.button import Button
    from limekit.widgets.checkbox import CheckBox
    assert Button().setText(42).getText() == CheckBox().setText(42).getText() == "42"


def test_listbox_accepts_a_python_list(qapp):
    """ListBox.setItems called .values() unconditionally and crashed on this."""
    from limekit.widgets.listbox import ListBox
    box = ListBox()
    box.setItems(["a", "b"])
    assert box.getItemsCount() == 2


def test_combobox_and_listbox_agree_on_setItems(qapp):
    from limekit.widgets.listbox import ListBox
    from limekit.widgets.combobox import ComboBox
    ListBox().setItems(["a", "b"])
    ComboBox().setItems(["a", "b"])          # neither may raise


def test_every_widget_shares_one_resize_rule(qapp):
    """BaseWidget had 7 size policies; ComboBox re-declared only 3."""
    from limekit.widgets.combobox import ComboBox
    from limekit.widgets.button import Button
    for widget in (ComboBox(), Button()):
        widget.setResizeRule("minimumexpanding", "preferred")


def test_combobox_callbacks_are_guarded(qapp, sink):
    """Only Button used to guard its callbacks."""
    from limekit.widgets.combobox import ComboBox
    box = ComboBox()
    box.setOnItemSelect(lambda *a: 1 / 0)
    box.setItems(["a", "b"])
    box.setCurrentIndex(1)
    assert len(sink) >= 1


def test_label_cursor_map_is_correct(qapp):
    from limekit.widgets.label import Label
    from PySide6.QtCore import Qt
    label = Label("x")
    label.setCursor("wait")
    assert label.cursor().shape() == Qt.CursorShape.WaitCursor
    label.setCursor("openhand")
    assert label.cursor().shape() == Qt.CursorShape.OpenHandCursor


def test_widgets_are_registered(qapp):
    from limekit.kernel.registry import registry
    import limekit.widgets.button, limekit.widgets.label          # noqa: F401
    import limekit.widgets.checkbox, limekit.widgets.listbox      # noqa: F401
    import limekit.widgets.combobox                               # noqa: F401
    for path in ("ui.Button", "ui.Label", "ui.CheckBox", "ui.ListBox", "ui.ComboBox"):
        assert registry.get(path) is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/widgets/test_pilot_widgets.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'limekit.widgets'`

- [ ] **Step 3: Write minimal implementation**

```python
# limekit/widgets/__init__.py
```

```python
# limekit/widgets/base.py
"""Shared widget behaviour, declared once.

Replaces BaseWidget, whose pass-through overrides added nothing and which
half the widget set did not inherit from anyway.
"""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QSizePolicy

from limekit.kernel.coerce import SIZE_POLICIES, Enum
from limekit.kernel.declarative import LimeObject
from limekit.kernel.spec import Prop

_size_policy = Enum(SIZE_POLICIES, "size policy")


class LimeWidget(LimeObject):
    """Mixin for every QWidget subclass exposed to Lua."""

    enabled = Prop(bool, default=True, qt=("isEnabled", "setEnabled"))
    visible = Prop(bool, default=True, qt=("isVisible", "setVisible"))
    toolTip = Prop(str, default="", qt=("toolTip", "setToolTip"), coerce=str)
    styleSheet = Prop(str, default="", qt=("styleSheet", "setStyleSheet"), coerce=str)

    def setResizeRule(self, horizontal, vertical):
        """One definition, seven policies - not three in some widgets."""
        self.setSizePolicy(QSizePolicy(
            _size_policy(horizontal), _size_policy(vertical)
        ))
        return self

    def setSize(self, width, height):
        self.resize(int(width), int(height))
        return self

    def setFixedSize(self, width, height):
        super().setFixedSize(QSize(int(width), int(height)))
        return self

    def setLocation(self, x, y):
        self.move(int(x), int(y))
        return self

    def setBackgroundColor(self, colour):
        self.setStyleSheet(f"background-color: {colour};")
        return self
```

```python
# limekit/widgets/button.py
from PySide6.QtWidgets import QPushButton

from limekit.kernel.coerce import Icon
from limekit.kernel.spec import Event, Prop
from limekit.widgets.base import LimeWidget


class Button(LimeWidget, QPushButton):
    __lime__ = "ui.Button"

    text = Prop(str, default="Button", qt=("text", "setText"), coerce=str,
                doc="the button's caption")
    icon = Prop(object, qt=("icon", "setIcon"), coerce=Icon)
    flat = Prop(bool, default=False, qt=("isFlat", "setFlat"))
    checkable = Prop(bool, default=False, qt=("isCheckable", "setCheckable"))
    checked = Prop(bool, default=False, qt=("isChecked", "setChecked"))

    onClick = Event("clicked", passes_self=True, doc="Fired when clicked.")

    def __init__(self, text="Button"):
        super().__init__()
        self.setText(text)
```

```python
# limekit/widgets/label.py
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel

from limekit.kernel.coerce import ALIGNMENTS, CURSORS, Enum
from limekit.kernel.spec import Prop
from limekit.widgets.base import LimeWidget

_alignment = Enum(ALIGNMENTS, "alignment")
_cursor = Enum(CURSORS, "cursor")


class Label(LimeWidget, QLabel):
    __lime__ = "ui.Label"

    text = Prop(str, default="", qt=("text", "setText"), coerce=str)
    wordWrap = Prop(bool, default=False, qt=("wordWrap", "setWordWrap"))
    textAlignment = Prop(object, qt=("alignment", "setAlignment"), coerce=_alignment)

    def __init__(self, text=""):
        super().__init__()
        self._image_path = ""
        self.setText(text)

    def setCursor(self, cursor):
        """Shared cursor map - the old one defined 'openhand' twice and
        mapped 'wait' to an arrow."""
        super().setCursor(_cursor(cursor))
        return self

    def setImage(self, path):
        self._image_path = path
        self.setPixmap(QPixmap(path))
        return self

    def getImagePath(self):
        return self._image_path
```

```python
# limekit/widgets/checkbox.py
from PySide6.QtWidgets import QCheckBox

from limekit.kernel.spec import Event, Prop
from limekit.widgets.base import LimeWidget


class CheckBox(LimeWidget, QCheckBox):
    __lime__ = "ui.CheckBox"

    text = Prop(str, default="", qt=("text", "setText"), coerce=str)
    checked = Prop(bool, default=False, qt=("isChecked", "setChecked"))

    onCheck = Event("clicked", passes_self=True)

    def __init__(self, text=""):
        super().__init__()
        self.setText(text)
```

```python
# limekit/widgets/listbox.py
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QListWidget, QListWidgetItem

from limekit.kernel.bridge.convert import as_sequence
from limekit.kernel.coerce import LuaIndex
from limekit.kernel.spec import Event
from limekit.widgets.base import LimeWidget


class ListBox(LimeWidget, QListWidget):
    __lime__ = "ui.ListBox"

    onItemSelect = Event("currentItemChanged", passes_self=True)
    onItemDoubleClick = Event("itemDoubleClicked", passes_self=True)

    def __init__(self, items=None):
        super().__init__()
        self.setAlternatingRowColors(True)
        if items is not None:
            self.setItems(items)

    def setItems(self, items):
        """Accepts a Lua table OR a Python sequence.

        The old implementation called .values() unconditionally and crashed
        on a Python list, unlike ComboBox.
        """
        self.clear()
        for item in as_sequence(items):
            self.addItem(QListWidgetItem(str(item)))
        return self

    def addImageItem(self, label, image):
        item = QListWidgetItem(str(label))
        item.setIcon(QIcon(image))
        self.addItem(item)
        return self

    def getItemsCount(self):
        return self.count()

    def getItemAt(self, index):
        """1-indexed, like every other Limekit collection accessor."""
        item = self.item(LuaIndex(index))
        return item.text() if item else None
```

```python
# limekit/widgets/combobox.py
from PySide6.QtWidgets import QComboBox

from limekit.kernel.bridge.convert import as_sequence
from limekit.kernel.coerce import LuaIndex
from limekit.kernel.spec import Event, Prop
from limekit.widgets.base import LimeWidget


class ComboBox(LimeWidget, QComboBox):
    __lime__ = "ui.ComboBox"

    editable = Prop(bool, default=False, qt=("isEditable", "setEditable"))

    onItemSelect = Event("currentIndexChanged", passes_self=True)

    def __init__(self, items=None):
        super().__init__()
        if items is not None:
            self.setItems(items)

    def setItems(self, items):
        self.clear()
        for item in as_sequence(items):
            self.addItem(str(item))
        return self

    def getText(self):
        return self.currentText()

    def getItemAt(self, index):
        return self.itemText(LuaIndex(index))
```

Regenerate the derived files, which now have real content to describe:

```bash
python tools/generate_manifest.py
python tools/generate_lua.py
python tools/generate_stubs.py
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/ -v`
Expected: PASS — including Tasks 12–14, whose generated files are no longer empty.

- [ ] **Step 5: Commit**

```bash
git add limekit/widgets/ tests/widgets/ limekit/kernel/manifest.py limekit/runtime/lua/
git commit -m "feat(widgets): migrate five pilot widgets to declarative specs"
```

---

### Task 17: Demo smoke suite

The ~40 demo projects are an integration corpus that is currently never run.

**Files:**
- Create: `tests/test_demo_smoke.py`

**Interfaces:**
- Consumes: `LimekitApp`
- Produces: a parametrised test per demo project that has a `scripts/main.lua`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_demo_smoke.py
"""Boot every demo project headless.

Demos live outside the repo, so this skips cleanly when they are absent.
Point LIMEKIT_DEMOS at the checkout to run them.
"""

import os
from pathlib import Path

import pytest

DEMOS = Path(os.environ.get(
    "LIMEKIT_DEMOS",
    Path(__file__).resolve().parents[2] / "limekit-demos",
))


def demo_projects():
    if not DEMOS.is_dir():
        return []
    return sorted(p.parent.parent for p in DEMOS.glob("*/scripts/main.lua"))


@pytest.mark.skipif(not demo_projects(), reason="limekit-demos checkout not found")
@pytest.mark.parametrize("project", demo_projects(), ids=lambda p: p.name)
def test_demo_boots_without_error(project, qapp):
    from limekit.kernel.app import LimekitApp

    with LimekitApp(project) as app:
        app.load_project()
        assert app.errors == (), f"{project.name} reported: {app.errors}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_demo_smoke.py -v`
Expected: FAIL — the demos still use the 1.x flat-global API (`Window{...}`, `VLayout()`), which no longer exists. Every demo reports `LuaError`.

- [ ] **Step 3: Write minimal implementation**

This task's deliverable is the harness plus an honest record of what does not yet pass.

**No demo is migrated in P0.** The calculator needs `ui.Window` and `ui.TextField`;
`Window` is deliberately excluded from the Task 16 pilot set because its hand-written
event overrides need the `Method` spec plumbing that P1 introduces. Migrating demos
is P1 work. Every demo therefore `xfail`s, and the xfail count is the P1 backlog.

```python
@pytest.mark.skipif(not demo_projects(), reason="limekit-demos checkout not found")
@pytest.mark.parametrize("project", demo_projects(), ids=lambda p: p.name)
def test_demo_boots_without_error(project, qapp):
    from limekit.kernel.app import LimekitApp

    # Every demo still uses the 1.x flat-global API. P1 migrates them; until
    # then this suite exists to measure the gap, not to hide it.
    pytest.xfail(f"{project.name} uses the 1.x API - migrate in P1")

    with LimekitApp(project) as app:
        app.load_project()
        assert app.errors == (), f"{project.name} reported: {app.errors}"
```

Also build `sys.evalExpression`, which replaces the `eval` builtin that P0 removes
from Lua globals (`app_engine.py` injected `builtins.eval`; the calculator demo
called it). Create `limekit/toolkit/text.py`:

```python
# limekit/toolkit/text.py
"""Safe replacements for the Python builtins P0 stops injecting into Lua."""

import ast
import operator

from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError

_OPERATORS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def _evaluate(node):
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise BridgeError(f"only numbers are allowed, got {node.value!r}")
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.operand))
    raise BridgeError(
        f"{type(node).__name__} is not permitted in an expression"
    )


class Sys(LimeObject):
    __lime__ = "sys.Expr"

    @staticmethod
    def evalExpression(expression):
        """Arithmetic only. Never exposes builtins.eval to Lua."""
        try:
            tree = ast.parse(str(expression), mode="eval")
        except SyntaxError as exc:
            raise BridgeError(f"malformed expression: {expression!r}") from exc
        return _evaluate(tree)
```

Add a test for it in the same task:

```python
# tests/toolkit/test_text.py
import pytest
from limekit.toolkit.text import Sys
from limekit.kernel.errors import BridgeError


@pytest.mark.parametrize("expr,expected", [
    ("1 + 1", 2), ("2 * (3 + 4)", 14), ("-5 + 2", -3), ("7 / 2", 3.5),
])
def test_arithmetic(expr, expected):
    assert Sys.evalExpression(expr) == expected


@pytest.mark.parametrize("expr", [
    "__import__('os').system('echo pwned')",
    "open('/etc/passwd').read()",
    "[].__class__",
    "lambda: 1",
])
def test_code_execution_is_refused(expr):
    with pytest.raises(BridgeError):
        Sys.evalExpression(expr)


def test_malformed_expression_raises():
    with pytest.raises(BridgeError, match="malformed"):
        Sys.evalExpression("1 +")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_demo_smoke.py tests/toolkit/ -v`
Expected: XFAIL for every demo (that count is the P1 backlog), PASS for the 8
`evalExpression` tests.

- [ ] **Step 5: Commit**

```bash
git add tests/test_demo_smoke.py tests/toolkit/ limekit/toolkit/
git commit -m "test: add demo smoke harness and safe expression evaluator"
```

---

## Self-Review

**Spec coverage:**

| Spec section | Task |
|---|---|
| §3.1 package layout + dependency rule | 15 (enforcement), 2/5/16 (structure) |
| §3.2 metadata layer | 3, 4, 5, 6, 7 |
| §3.3 generation targets | 12 (manifest), 13 (limekit.lua), 14 (stubs) |
| §3.4 registry, manifest, namespacing | 8, 10, 12 |
| §3.4 no builtins in Lua globals | 10 (asserted), 17 (`sys.evalExpression`) |
| §3.5 bridge + 1-indexing | 4 (`LuaIndex`), 9 (`as_sequence`) |
| §3.6 lifecycle | 11 |
| §3.7 error handling + source mapping | 2, 7, 10 |
| §4 testing | 1, 15, 17 |
| §5 migration | 17 (partial — full demo migration is P1) |
| §1.2 defect table | 4 (cursor map), 9 (ListBox), 6 (coercion), 7 (guarding), 1 (deps) |

**Two gaps I am flagging rather than hiding:**

1. **`Window`'s four defects** (`onContextMenuEvent` AttributeError, `just_shown` unused, `closeEvent` not calling `super()`, `showEvent` re-centring) are **not** closed by any task here. `Window` is not in the Task 16 pilot set because it is a `QMainWindow` with hand-written event overrides, which needs the `Method` spec plumbing that P1 introduces. §7 item 8 of the spec claims the whole defect table is closed by P0 — that is now inaccurate. Either add a Task 18 migrating `Window`, or amend the spec's definition of done. **My recommendation: amend the spec**, since migrating `Window` properly belongs with the rest of the hierarchy work.

2. **`gui/threading.py:21`'s infinite recursion** is likewise untouched — `Thread` is P3 territory.

**Placeholder scan:** clean.

**Type consistency:** verified `Prop.accessor_names()` returns a 3-tuple everywhere it is consumed (Tasks 6, 14); `Event.setter_name()` used identically in Tasks 7 and 14; `registry.modules()` returns `dict[str, dict[str, type]]` in Tasks 8, 10, 13, 14; `as_sequence` returns `list` in Tasks 9 and 16.
