# Phase A: Service Layer — Report

## Summary

Built the six new modules under `limekit/services/` requested for Phase A
(the 1.x `app` table replacement), wired project-root discovery into
`LimekitApp.boot()`, updated `.importlinter`, regenerated all three
generated artifacts, and added a `tests/services/` suite.

## What was built

- `limekit/services/__init__.py` — empty package marker.
- `limekit/services/resources.py` — `res.Resources` (`__lime__`). Static
  `images`/`scripts`/`misc` path joiners plus `route(key)`, which ports 1.x's
  `core/routing/routes.py` single/group route schema. `route()` raises
  `RouteError` naming the key on any failure to resolve. Project root is
  held in a module slot set by `set_project_root(path)`, mirroring
  `bridge/convert.set_runtime`. Uses `ProjectError` if called before the
  root is set or if `app.json` is missing/malformed.
- `limekit/services/fs.py` — `fs.FileSystem` (`__lime__`). Full file/JSON/
  directory API from the spec. Every OS-level failure (`OSError`,
  `UnicodeDecodeError`, `json.JSONDecodeError`, etc.) is caught and
  re-raised as `BridgeError`; nothing crosses the bridge as a raw Python
  exception.
- `limekit/services/dialogs.py` — `ui.Dialogs` (`__lime__`). Wraps
  `QMessageBox`/`QInputDialog`/`QFileDialog`/`QColorDialog`/`QFontDialog`.
  Every "cancelled" path returns `None`; `question()` returns a real
  boolean.
- `limekit/services/system.py` — `sys.System` (`__lime__`). `execute()` runs
  under a 30s `subprocess.run(..., timeout=...)` and raises `BridgeError` on
  timeout or OS failure — 1.x's equivalent had no timeout and could hang the
  process indefinitely. Also covers OS/CPU/clipboard/hash/base64/emoji/
  standard-path helpers.
- `limekit/services/theming.py` — `ui.Theme` (`__lime__`). Ports all five
  1.x theme families (material, misc, darklight, darkstyle, qtthemes).
  Unlike 1.x — which printed a warning and silently no-op'd when an optional
  theming package (`qt_material`, `pyqtdarktheme`, `qdarkstyle`) was
  missing — this raises `BridgeError` naming the package to install. That
  silent-failure behavior was a real defect (a Lua script setting a theme
  that quietly does nothing), not something worth reproducing.

## Wiring

- `LimekitApp.boot()` now imports `limekit.services.resources` **inside the
  method** and calls `resources.set_project_root(self.project_path)`,
  keeping `kernel/` free of any module-level dependency on `services/`.
- `.importlinter`: added `limekit.services` to the kernel contract's
  `forbidden_modules`. grimp's static analysis flags import statements
  regardless of nesting, so the one sanctioned call site
  (`limekit.kernel.app -> limekit.services.resources`) is listed under a new
  `ignore_imports` entry on the same contract, with a comment explaining
  why. `tests/test_layering.py` passes.

## Corrected/completed behavior vs. 1.x

- **Group routing `group_label` (EIM)**: 1.x's `routes.py` documented
  "Exempt Individual Marking" (a group-level marker so items don't need
  their own `marker::resource` prefix) but never implemented it — the code
  path always required a per-item marker even when `group_label` was
  present, making the field dead weight. This build actually implements
  EIM. Covered by
  `test_group_route_with_group_label_resolves_without_per_item_marker`.
- **Optional theming packages**: see above — turned a silent no-op into a
  named `BridgeError`.
- **`sys.System.execute` timeout**: 1.x had none; this build bounds it at
  30s and raises `BridgeError` rather than risking an indefinite GUI-thread
  block.

Nothing else in the ported 1.x sources looked broken enough to warrant
deviating from behavior; the rest is a straightforward, bridge-safe
translation.

## Codegen

Ran, in order:
```
python tools/generate_manifest.py
python tools/generate_lua.py
python tools/generate_stubs.py
```
All three changed as expected (5 new `__lime__` classes registered).
Running the three generators a second time produced byte-identical output
(`git status --short` shows no further diff after the first regeneration) —
regeneration is a verified no-op.

## Tests

Added `tests/services/test_resources.py`, `test_fs.py`, `test_dialogs.py`,
`test_system.py`, `test_theming.py` (97 tests). Coverage includes: route
resolution (single, group, group+EIM, missing key, missing group, missing
item, unmarked single route), file round-trips and every listed failure
path raising `BridgeError` (not a raw `OSError`/`json.JSONDecodeError`),
dialogs returning `None` on cancel (via `monkeypatch` on the static
`QMessageBox`/`QInputDialog`/`QFileDialog`/`QColorDialog`/`QFontDialog`
methods — no real dialogs are opened), and theming's optional-dependency
`BridgeError` path (verified by monkeypatching `builtins.__import__` to
simulate the package being absent, since `qt_material`/`qdarkstyle`/
`pyqtdarktheme` are all actually installed in this environment).

## Test results

- Before: 194 passed, 52 xfailed
- After: 291 passed, 52 xfailed (97 new tests, zero regressions,
  `QT_QPA_PLATFORM=offscreen`)

## Not built / deferred

Nothing from the spec was skipped. All six requested modules, the
`LimekitApp.boot()` wiring, the `.importlinter` update, all three codegen
artifacts, and the test suite are complete.
