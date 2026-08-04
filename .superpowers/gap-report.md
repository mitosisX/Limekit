# Closing the last API gap for the Limekit 2.0 migration

## What was built

Five new `LimeObject` classes, all service-style (`LimeObject` + the bare Qt
class, not `LimeWidget`) because none of the underlying Qt types are
`QWidget`:

| Class | `__lime__` | File |
|---|---|---|
| `Timer` | `sys.Timer` | `limekit/services/timer.py` |
| `SysTray` | `ui.SysTray` | `limekit/services/systray.py` |
| `SysNotification` | `ui.SysNotification` | `limekit/services/sysnotification.py` |
| `DropShadow` | `ui.DropShadow` | `limekit/services/dropshadow.py` |
| `AutoComplete` | `ui.AutoComplete` | `limekit/services/autocomplete.py` |

All five were placed in `limekit/services/` alongside `dialogs.py`,
`concurrency.py`, etc. — the file location follows "is this a `QWidget`?",
not the `__lime__` module prefix (`ui.SysTray` still lives in `services/`,
matching how `ui.Dialogs` already does).

## Timer's interval unit

**Kept in milliseconds.** 1.x's `Timer.setInterval` passed its argument
straight into `QTimer.setInterval` with zero conversion — Qt's own unit,
unchanged. Any demo doing `Timer():setInterval(1000):start()` for a
one-second tick keeps ticking once a second, not once a millisecond, after
the rewrite. Silently rescaling to seconds would have been a breaking,
silent behavior change across every demo that touches a timer, which the
task explicitly called out to avoid.

One naming wrinkle: `QTimer.isSingleShot`/`setSingleShot` is a genuine
Qt getter/setter pair and became a `Prop`, but 1.x also exposed a *static*
`Timer.singleShot(msec, callback)` convenience (`QTimer.singleShot`) that
fires a callback once. Both are named `singleShot` in Qt/1.x. Declaring the
`Prop` under the Python attribute name `singleShot` would have had the
later `@staticmethod def singleShot` silently clobber the `Prop` object in
the class body before `__init_subclass__` ever saw it (last assignment
wins) — a real bug I caught by testing, not something the collision guard
catches, since the guard only fires at *accessor-installation* time, and
there'd have been no accessor to install. Fixed by declaring the `Prop`
under the Python name `single_shot` with `lua_name="singleShot"`, so the
generated Lua-facing accessors (`getSingleShot`/`setSingleShot`/
`isSingleShot`) are unaffected and the static method keeps its own name.
The static `singleShot`'s callback is now wrapped in `guard()` — 1.x
connected the raw Lua callable straight to `QTimer.singleShot`, so an
exception inside it would have escaped uncaught into the Qt event loop.

## Alias verdicts

Both suspected aliases were confirmed as the **same class under an older
name**, not a second widget:

- **`Dockable` → `ui.Dock`.** 1.x's `components/dockable/dockable_widget.py`
  declares `class Dock(QDockWidget, EnginePart): name = "Dockable"` — it's
  literally the `Dock` class, registered to Lua under the string
  `"Dockable"`. The already-migrated `ui.Dock` (`limekit/widgets/dock.py`)
  covers the same surface (title, icon, floating, child, layout, allowed
  areas, features) and then some. Registered as a second path:
  `registry.register("ui.Dockable", Dock)` at the bottom of `dock.py`.

- **`ChartCanvas` → `chart.ChartView`.** 1.x's
  `components/charts/chartview.py` declares
  `class ChartCanvas(QChartView, EnginePart)` with a `chart` constructor
  arg, `setTheme`/`getThemes`. The already-migrated `chart.ChartView`
  (`limekit/charts/chartview.py`) is the same wrapper around the same
  `QChartView`. Registered as a second path:
  `registry.register("chart.ChartCanvas", ChartView)` at the bottom of
  `chartview.py`.

`Registry.register` was confirmed to tolerate this: the collision check in
`registry.py` is keyed per *path*, not per *class* — `existing is not
cls` only fires when the **same path** is registered to a **different**
class. Two different paths pointing at the same class never trip it, so no
thin-subclass workaround was needed for either alias. Both generators
(`generate_lua.py`, `generate_stubs.py`) already group by
`registry.modules()`, which iterates `(path, cls)` pairs independently, so
the alias paths show up as their own entries (`Dockable`, `ChartCanvas`)
in the generated `.lua` stubs pointing at the identical class — verified by
inspecting `limekit/runtime/lua/stubs/ui.lua` and `stubs/chart.lua` after
regeneration.

## 1.x defects found and *not* reproduced

- **`SysNotification.setMessage` swallowed messages on tray-less
  systems.** 1.x checked `isSystemTrayAvailable()` and, if false, did
  `print("No System Tray available")` instead of calling
  `showMessage`. On a headless CI box (or a Linux session with no tray
  daemon) every single notification was silently dropped, visible only as
  a stray console `print` that no Lua caller could ever see or handle.
  The 2.0 `SysNotification.showMessage` always calls through to Qt's
  `showMessage`; if the platform genuinely can't show it, that's Qt's
  call, not something to hide from the caller behind a print statement.

- **1.x `DropShadow.__init__` did `self = QGraphicsDropShadowEffect(self)`
  inside its own constructor** — after `super().__init__()` had already
  built the real effect object, this rebound the *local* name `self` to a
  second, brand-new, never-attached, never-returned effect, then
  proceeded to configure and attach *that* one. Since `self =` inside
  `__init__` never affects the object the caller actually holds a
  reference to, half of that constructor was configuring and discarding a
  second object every single time — pure dead code that happened to still
  work because the *original* `self` (parent-attached via
  `EnginePart.__init__`) was left with Qt's blur/color/offset defaults, not
  the intended `#7090B0`-at-20%-alpha look, unless nothing downstream
  actually depended on those values being anything but defaults. Rewritten
  so there is exactly one effect object, and its blur/color/offset are the
  1.x intended defaults (now overridable via `Prop`s) rather than an
  accident of which of two objects Qt happened to keep alive.

- **1.x `Thread.sleep(self): self.sleep()`** — already documented and not
  reproduced in `limekit/services/concurrency.py` from a prior phase; not
  part of this gap but noted here for completeness since it's the same
  "don't reproduce a defect just because it's in 1.x" category.

## Headless caveats

`SysTray` and `SysNotification` wrap `QSystemTrayIcon`, which does not
reliably work under `QT_QPA_PLATFORM=offscreen` (no system tray daemon in
CI). `tests/widgets/test_utilities.py` asserts *construction* and prop
round-trips unconditionally (that's what the demos need), and gates only
the two behaviors that actually require a live tray
(`onActivated`/`showMessage` firing for real) behind
`@pytest.mark.skipif(not QSystemTrayIcon.isSystemTrayAvailable(), ...)`
with a stated reason, rather than deleting them or faking a pass.

## Verification

- `tools/generate_manifest.py`, `generate_lua.py`, `generate_stubs.py` were
  all re-run after adding the five classes and the two alias
  registrations; running them a second time in a row produced no further
  diff (`git status --short` clean save for the new/edited source files
  and the untracked `.superpowers/*.md` phase reports from prior work).
- `python -m lint_imports` (import-linter): both contracts (`kernel imports
  nothing from the rest of limekit`, `strict layering`) still **KEPT**.
- Full suite: **384 passed / 52 xfailed → 409 passed / 52 xfailed / 2
  skipped** (the 25 new non-skipped tests in `test_utilities.py`, plus 2
  skipped for the no-tray-in-CI reason above).
