# Limekit 2.0 — P0 Kernel Design

**Date:** 2026-08-03
**Status:** Approved for planning
**Scope:** P0 of a 7-part program. This spec covers the kernel only.

---

## 1. Context

Limekit is a Lua GUI framework. PySide6 supplies Qt widgets; `lupa` injects Python
classes into a Lua runtime as globals; users write pure Lua. The codebase is roughly
12,300 lines across ~120 Python modules, with **118** `EnginePart` subclasses and
**95** hand-written `app.*` Lua functions. There are no tests.

The framework works. Its problems are structural, not functional, and they all trace
back to four decisions in the kernel.

### 1.1 Problems this spec fixes

**P1 — Class discovery loads modules by file path.**
`Engine.load_classes()` (`app_engine.py:611`) uses `importlib.util.spec_from_file_location`,
so a module can exist twice under two identities and `issubclass(cls, EnginePart)`
silently returns `False`. Load order is filesystem-dependent. `settings.IGNORE_PARTS`
is declared and never referenced anywhere in the codebase.

**P2 — Dev and frozen modes use different discovery.**
Development walks the filesystem. Frozen (PyInstaller) uses a hand-maintained
130-entry list at `app_engine.py:399-531`. Adding a widget without updating that list
produces a build that works in development and silently lacks the widget when shipped.

**P3 — The API has three sources of truth.**
Every user-facing utility must exist as a Python class, as an entry in
`limekit/lua/limekit.lua`, and as an entry in `limekit/lua/script.py` — which is a
byte-identical dead duplicate of `limekit.lua`. Nothing enforces agreement.

**P4 — Inheritance is cosmetic.**
`BaseWidget` is a mixin whose methods call `super()` on methods it does not own; it
resolves only by MRO accident, and roughly half its methods (`hide`, `show`,
`setVisible`, `setEnabled`, `setStyleSheet`) are pure pass-throughs. Several widgets
skip it entirely — `ComboBox(QComboBox, EnginePart)`, `Window(QMainWindow, EnginePart)`,
`GridLayout(QGridLayout, EnginePart)` — and re-implement its methods with different
behaviour. `setResizeRule` exists twice: 7 size policies in `BaseWidget`, 3 in
`ComboBox`. `EnginePart` itself is a marker class carrying a `__str__` and an unused
`premium` flag.

**P5 — Event callbacks are inconsistently guarded.**
`Button.__handleOnClick` wraps callbacks in `try/except` → `handle_widget_error`.
`ComboBox`, `ListBox`, `Label` and every `Window` event handler do not. An error in
one of those propagates into the Qt event loop.

**P6 — Import-time side effects make the framework untestable.**
`App.app = QApplication(sys.argv)` runs at class-definition time.
`error_handler = LimekitErrorHandler()` runs at import. `runner.py` instantiates and
runs the application at module scope, and `main.py` is `from limekit.runner import *`.
`import limekit` launches Qt. This is the direct cause of there being no tests.

**P7 — Conversion is ad hoc and has already diverged.**
`ComboBox.setItems` guards with `lupa.lua_type(items) == "table"`; `ListBox.setItems`
calls `.values()` unconditionally and therefore crashes on a Python list.
Lua/Python indexing is inconsistent *within the framework*: `BaseLayout.getChildAt`
and `GridLayout.getAt` subtract 1; `ListBox.getItemAt` and `ComboBox.setCurrentIndex`
do not.

### 1.2 Concrete defects produced by the above

| Location | Defect |
|---|---|
| `components/widgets/window.py:291` | `onContextMenuEvent` is read but never declared as a class attribute → `AttributeError` unless `setOnContextMenu` was called first |
| `components/widgets/window.py:230` | `showEvent` calls `center()` on every show; the `just_shown` guard is declared and never used, so re-showing a window yanks it back to centre |
| `components/widgets/window.py:240` | `closeEvent` never calls `super()` and never accepts or ignores the event |
| `gui/threading.py:21` | `def sleep(self): self.sleep()` — unconditional infinite recursion |
| `components/widgets/label.py:105,107` | `"openhand"` defined twice in the cursor dict (second wins → `CustomCursor`); `"wait"` maps to `ArrowCursor` |
| `utils/converters.py:110` | Unreachable code after `return` |
| `components/widgets/listbox.py:52` | `items.values()` unconditional → crashes on a Python list |
| `engine/app_engine.py:11` | Imports `playsound`, which is absent from `requirements.txt`; `setup.py` and `requirements.txt` disagree on dependencies |
| `engine/app_engine.py` | `eval`, `str`, `int`, `dict`, `tuple`, `print`, `len` injected as Lua globals; `Converter.py_indexing` calls `eval()` on user input |

### 1.3 Decisions already taken

- **Backward compatibility:** clean break at 2.0. Existing `.lua` apps migrate via codemod.
- **Approach:** metadata-driven kernel (declarative specs, generated accessors), not a
  thin registry-only fix and not a full reactive descriptor DSL.
- **Generated code:** emitted to committed `_generated.py` files, with a CI check that
  regeneration is a no-op. Not installed invisibly at runtime.

---

## 2. Validated assumptions

A spike (`spike_metaclass.py`) confirmed the following against PySide6 6.11.0,
lupa 2.8, Python 3.13:

| Assumption | Result |
|---|---|
| `__init_subclass__` on a mixin combined with a Shiboken base | Works |
| Accessors installed onto the class at class-creation time | Works |
| Plain Python descriptors on a `QWidget` subclass | Works |
| A naive custom metaclass on a `QWidget` subclass | **Fails** — `TypeError: metaclass conflict`. Must subclass `type(QWidget)`. **Therefore: use `__init_subclass__`, never a metaclass.** |
| Lua calling a *generated* method through lupa | Works — lupa cannot distinguish generated from hand-written |
| Namespaced Lua module tables in place of flat globals | Works |
| Lua attaching arbitrary fields to a Python widget instance | Works (relevant to P2's component model) |
| 8 threads concurrently executing on one `LuaRuntime` | No errors, no corruption — lupa 2.8 serialises behind a lock. It does **not** parallelise. Qt mutation must still occur on the GUI thread. Deadlock behaviour under Qt slot re-entrancy is **not** established by this spike and must be verified during P3. |

A second spike (`spike_shadowing.py`) surfaced two constraints that the design must
honour. Both were found by testing, not by inspection, and both silently break the
generated accessors if ignored.

**C1 — Spec objects shadow the Qt attributes they describe.**
Declaring `text = Prop(...)` in a class body shadows `QPushButton.text`, so
`instance.text` yields the `Prop` object rather than the bound Qt method. The collector
**must `delattr` every `Prop`/`Event` from the class after collecting it**, allowing the
Qt attribute to resurface through the MRO. Verified: after cleanup, `b.text` is again a
`builtin_function_or_method`.

**C2 — Qt methods must be bound at generation time, not looked up at call time.**
A `Prop` named `text` generates a setter called `setText` — the same name as the Qt
method it needs to call. If the generated setter does `getattr(self, "setText")(value)`
it resolves to *itself* and recurses. The generator must capture the underlying
functions before installing anything:

```python
qt_get_fn = getattr(cls, prop.qt[0])   # resolve BEFORE setattr shadows it
qt_set_fn = getattr(cls, prop.qt[1])

def setter(self, value, _s=qt_set_fn, _c=prop.coerce):
    return _s(self, _c(value) if _c else value)
```

Verified with this fix: coercion applies (`setText(42)` → `'42'`), a subclass may
override an inherited `Prop` without corrupting the parent, and a raising Lua handler is
contained by the guard rather than escaping into the Qt event loop.

---

## 3. Architecture

### 3.1 Package layout

```
limekit/
├── kernel/                  # depends on nothing else in limekit
│   ├── spec.py              # Prop · Event · Method (inert specs) + coercions
│   ├── declarative.py       # __init_subclass__ collector + accessor generation
│   ├── registry.py          # single source of truth: dotted name → class + metadata
│   ├── manifest.py          # GENERATED import list; used by dev AND frozen
│   ├── bridge/
│   │   ├── convert.py       # all Lua↔Python marshalling
│   │   ├── runtime.py       # owns LuaRuntime; installs namespaced modules
│   │   └── guard.py         # the single guarded seam for Lua callbacks
│   ├── errors.py            # exception taxonomy + source-mapped tracebacks
│   └── app.py               # LimekitApp — explicit lifecycle
│
├── widgets/  layouts/  dialogs/  charts/     # internals reshaped in P1
├── services/                # formerly core/
│   ├── clipboard.py  timer.py  tray.py  notifications.py
│   ├── storage/  routing/  theming/
├── toolkit/                 # formerly utils/ + non-widget half of gui/
│   ├── fs.py  paths.py  text.py  encoding.py  system.py  sound.py
│   └── typography.py  keys.py  colors.py
├── build/                   # unchanged in P0
└── runtime/lua/             # limekit.lua is GENERATED, never hand-edited
```

**Dependency rule:** `kernel` imports nothing from `widgets`, `services` or `toolkit`.
Everything else imports `kernel`. No cycles. Enforced by an import-linter test in CI.

This deletes `GlobalEngine`. That singleton exists solely to break a circular import —
`app_engine.py:22` says so directly: *"Was experiencing circular import in Converter,
thats why I am separating the engine for global use."* With the layering enforced, the
runtime is injected rather than reached for.

### 3.2 The metadata layer

Three inert spec types. No descriptor protocol, no metaclass.

```python
# kernel/spec.py
class Prop:
    def __init__(self, type_, *, default=None, qt=None,
                 coerce=None, validate=None, doc="", lua_name=None): ...

class Event:
    def __init__(self, qt_signal, *, passes_self=True, args=(), doc=""): ...

class Method:
    def __init__(self, *, qt=None, doc="", lua_name=None): ...
```

Alongside them, `spec.py` defines the **coercion vocabulary** — small callables a `Prop`
names via `coerce=`. These are not spec types; they are the conversion functions the
generated setter applies before handing a value to Qt:

| Coercion | Purpose |
|---|---|
| `Icon` | path string, `QIcon`, or standard-icon name → `QIcon` |
| `Size` | `{w, h}` Lua table or two args → `QSize` |
| `Colour` | hex string, name, or RGB table → `QColor` |
| `LuaIndex` | 1-based Lua index → 0-based Qt index (see §3.5) |
| `Enum(map)` | case-insensitive string → Qt enum, from one shared map |

`Enum(map)` is what collapses the alignment, cursor, dock-area, toolbar-area and
size-policy lookup tables that are currently re-declared — and divergent — across
`BaseLayout`, `Label`, `Window` and `ComboBox`.

Widgets declare rather than implement:

```python
class Button(ButtonLike):
    __lime__ = "ui.Button"

    text    = Prop(str,  default="Button", qt=("text", "setText"), coerce=str)
    icon    = Prop(Icon, qt=("icon", "setIcon"), coerce=QIcon)
    flat    = Prop(bool, default=False, qt=("isFlat", "setFlat"))
    checked = Prop(bool, default=False, qt=("isChecked", "setChecked"))

    onClick = Event("clicked", passes_self=True)
```

At class creation `__init_subclass__` walks the reversed MRO, collects every `Prop`,
`Event` and `Method` (so subclasses inherit parent specs and may override them by
name), and generates accessors. Those four declarations produce `setText`/`getText`,
`setIcon`/`getIcon`, `setFlat`/`isFlat`, `setChecked`/`isChecked` and `setOnClick` —
each wrapped in the error guard — plus the LSP stub entry and the docs entry.

Three consequences:

- **Coercion is central.** `Button.setText` currently calls `str(text)` by hand;
  `CheckBox.setText` does not, so `CheckBox(42)` and `Button(42)` behave differently.
  `coerce=str` on the spec makes that structural.
- **Guarding is not optional.** There is no unguarded path to attach a handler; the
  generated setter is the only one.
- **Divergence is impossible.** A shared `Prop` on a base class cannot fork into a
  7-policy and a 3-policy version.

### 3.3 Generation targets

All produced from one registry walk, all committed, all covered by golden-file tests:

| Target | Replaces |
|---|---|
| `runtime/lua/limekit.lua` | the hand-written 340-line file (95 functions) |
| `runtime/lua/*.lua` LSP stubs | nothing — new capability, consumed by P5 |
| `kernel/manifest.py` | the hand-maintained 130-entry frozen list |
| API reference docs | nothing — new |
| `limekit/lua/script.py` | **deleted** — dead byte-identical duplicate |

### 3.4 Registry, manifest and namespacing

`__lime__ = "ui.Button"` *is* the registration; `__init_subclass__` files the class
into the registry under its dotted path. No decorator.

The manifest generator scans the tree for `__lime__` and emits an explicit import list
to `kernel/manifest.py`, committed to git. Dev and frozen both call
`import_all(manifest.MODULES)` — one code path. A CI test asserts regeneration is a
no-op, converting P2 from a shipping defect into a failing test.

Lua sees namespaced modules via `package.preload` entries fed from the registry:

```lua
local ui  = require("limekit.ui")
local fs  = require("limekit.fs")
local sys = require("limekit.sys")

local win = ui.Window { title = "Hello", size = {800, 600} }
local btn = ui.Button { text = "Click me" }
```

The `__`-prefixed pseudo-private globals are removed; they were a naming convention
standing in for a module system.

Python builtins are no longer injected into Lua globals. `eval` in particular is
`builtins.eval` exposed to every script, and `Converter.py_indexing` calls
`eval(f"{input_data}{index_spec}")` on user input. Replacement: `sys.evalExpression(s)`,
backed by an AST evaluator restricted to arithmetic nodes.

### 3.5 The bridge

```python
# kernel/bridge/convert.py
to_lua(value)        # py → lua: list / dict / tuple / set / generator / None
to_py(value)         # lua → py: table (array vs map detected), nil, function
as_sequence(value)   # Lua table OR Python sequence → list
as_mapping(value)
as_callable(value)   # wraps a Lua function for safe invocation from Python
```

`as_sequence` is the important one: every widget accepting items routes through it, so
Lua tables and Python sequences both work uniformly. That is the `ListBox`/`ComboBox`
divergence eliminated by construction.

**Indexing gets one rule: the Lua API is 1-indexed everywhere**, applied by a `LuaIndex`
coercion at the spec level rather than by per-method arithmetic.

Deleted here: the unreachable code in `Converter.list_`, the two near-duplicate
`py_kwargs` implementations, and the `table(x)[1]` idiom in `to_lua_table`.

### 3.6 Lifecycle

```python
class LimekitApp:
    def __init__(self, project_path, *, argv=None, frozen=None)
    def boot(self) -> None          # QApplication → registry → runtime → modules
    def load_project(self) -> None  # routes, package.path, main.lua
    def run(self) -> int            # event loop; returns exit code
    def shutdown(self) -> None
    def __enter__ / __exit__        # context manager, for tests
```

`sys.exit` moves to a thin `__main__.py`. `destroy_engine()` — currently `sys.exit()`
called from a `finally` block during cleanup — is replaced by real teardown.

### 3.7 Error handling

`kernel/bridge/guard.py` is the only path a Lua callable takes into Python. It catches,
classifies, attaches the originating widget and event name, and never allows an
exception to reach the Qt event loop.

Lua chunks are named after their real source file when passed to `execute()`, so
tracebacks read `scripts/main.lua:47` rather than `[string "<python>"]:47`. This deletes
the string-surgery (`error_str.rfind('>"]')`) currently duplicated in both `runner.py`
and `error_handler.py`.

`kernel/errors.py` defines:

```
LimekitError
├── BridgeError
├── RegistryError
├── ProjectError
├── RouteError
├── LuaError
└── WidgetCallbackError
```

This replaces the 10-branch `except` ladder in `runner.py` with dispatch on a type.

---

## 4. Testing

P0 ships the harness, since none exists.

- `pytest` + `pytest-qt`, `QT_QPA_PLATFORM=offscreen` (spike-confirmed headless)
- **Kernel units:** spec collection, MRO override semantics, accessor generation,
  registry behaviour, conversion round-trips, guard behaviour
- **Golden-file tests** on all generated output; drift fails the build
- **Import-linter test** enforcing the §3.1 dependency rule
- **Manifest completeness test** — catches the frozen-mode divergence class
- **Headless demo smoke suite:** boot `LimekitApp` against each of the ~40 demo
  projects and assert no exception

The demo suite is the highest-value item: those projects already exist and constitute
a free integration corpus that is currently never run.

---

## 5. Migration

| Breaks | Provided |
|---|---|
| Flat globals → `require("limekit.ui")` | `limekit migrate` codemod (mechanical) |
| `__`-prefixed globals removed | namespaced equivalents |
| `eval`/`str`/`int`/`dict`/`tuple`/`print`/`len` no longer global | `sys.evalExpression` and `sys.*` equivalents |
| Indexing normalised to 1-based | codemod flags sites it cannot prove |
| `limekit/lua/script.py` | deleted |

The demos are the migration corpus: run the codemod over them, run the headless smoke
suite, and the resulting diff *is* the migration guide.

---

## 6. Out of scope for P0

Named here so they are not silently absorbed. Each gets its own spec.

| Phase | Scope |
|---|---|
| **P1** | Widget hierarchy: real base chain, traits, declarative props applied across all widgets |
| **P2** | Component model and reactive state |
| **P3** | Concurrency: worker API, cancellation, GUI-thread marshalling, async HTTP |
| **P4** | Theming: design tokens, theme schema, variants, runtime switching |
| **P5** | DX: LSP stubs consumed, source-mapped tracebacks surfaced, hot reload rework |
| **P6** | Surface expansion: additional widget methods and toolkit functions |

P0 deliberately does **not** decide reactivity semantics. Doing so before P2 exists
would commit the kernel to a model with no consumer to validate it against.

---

## 7. Definition of done

1. `import limekit` has no side effects; no `QApplication` is constructed at import.
2. `kernel/` passes the import-linter rule; `GlobalEngine` no longer exists.
3. `manifest.py` regeneration is a verified no-op in CI.
4. `limekit.lua` and the LSP stubs are generated; `lua/script.py` is deleted.
5. Every Lua callback crosses `guard.py`; no unguarded handler-attachment path exists.
6. A Lua error reports its real `.lua` file and line, with no string-surgery in the path.
7. All ~40 demo projects boot headless without exception under the migrated API.
8. The following rows of the §1.2 defect table are closed, each with a regression
   test: the `label.py` cursor map, the `listbox.py` sequence handling, the
   `converters.py` dead code, the `CheckBox`/`Button` coercion split, the unguarded
   callbacks, the injected builtins, and the `playsound` dependency gap.

   **Explicitly not closed by P0**, because they depend on machinery later phases
   introduce:

   - The four `Window` defects (`onContextMenuEvent`, `just_shown`, `closeEvent`,
     `showEvent` re-centring). `Window` is a `QMainWindow` with hand-written event
     overrides and needs the `Method` spec plumbing from **P1**.
   - `gui/threading.py:21`'s infinite recursion — **P3**.
