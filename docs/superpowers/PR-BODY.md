# P0: Declarative metadata kernel for Limekit 2.0

First phase of a seven-part 2.0 rework. Replaces path-based class discovery, hand-written
Lua bindings, and import-time side effects with a kernel that generates its own bindings,
stubs, and frozen-mode manifest from one registry.

**32 commits · 145 tests passing (from zero) · 52 xfailed by design**

---

## What changed

Widgets now **declare** their surface instead of hand-writing accessors:

```python
class Button(LimeWidget, QPushButton):
    __lime__ = "ui.Button"
    text    = Prop(str, qt=("text", "setText"), coerce=str)
    flat    = Prop(bool, qt=("isFlat", "setFlat"))
    onClick = Event("clicked", passes_self=True)
```

That produces `getText`/`setText`, `getFlat`/`isFlat`/`setFlat`, and a guarded
`setOnClick` — plus the LSP stub entry and the manifest line. One source, four outputs.

Lua sees namespaced modules instead of ~138 flat globals:

```lua
local ui = require("limekit.ui")
local btn = ui.Button { text = "Click me" }
```

## Defects closed

| Was | Now |
|---|---|
| `label.py` defined `"openhand"` twice; `"wait"` → `ArrowCursor` | one shared `CURSORS` map |
| `ListBox.setItems` crashed on a Python list; `ComboBox` didn't | both route through `as_sequence` |
| `CheckBox.setText` skipped the `str()` coercion `Button` applied | `coerce=str` on the spec |
| `setResizeRule`: 7 policies in `BaseWidget`, 3 in `ComboBox` | one definition |
| Only `Button` guarded its callbacks | no unguarded path through generated accessors |
| Dev walked the filesystem; frozen used a hand-kept 130-entry list | one generated manifest, regeneration verified |
| `limekit.lua` duplicated byte-identically in `script.py` | generated; duplicate deleted |
| `import limekit` launched Qt | explicit `LimekitApp` lifecycle |
| Lua errors parsed via `error_str.rfind('>"]')` in two files | structured `.source` / `.line` |
| `playsound` imported but undeclared | dependencies reconciled |

## Security

`lupa` installs a `python` table by default containing `python.eval` and
`python.builtins`, so **arbitrary Python was reachable from any Lua script** — verified:
`python.builtins.open("setup.py").read()` succeeded. Now constructed with
`register_eval=False, register_builtins=False`.

`sys.evalExpression` replaces the `builtins.eval` that 1.x injected as a Lua global:
an allowlist-by-default AST walk permitting only arithmetic, with a magnitude bound so
`9**9**9` is refused in ~0.1ms rather than hanging the process.

## Compatibility

The legacy 1.x trees (`engine/`, `components/`, `core/`, `utils/`, `gui/`) are untouched
and still import — existing apps keep running. They retire in P1. An import-linter
contract plus a grep test enforce that `kernel/` never depends on them.

## Known limitations

- **All 52 demo projects xfail.** They use the 1.x API; migrating them is P1. The xfail
  count is the backlog size, deliberately not hidden behind a green suite.
- **No CI exists.** The three regeneration no-op checks that catch stale generated
  artifacts are local-only until a workflow runs them.
- **`python.as_attrgetter` remains an escape hatch** — it can reach a widget's Qt signal
  and attach an unguarded handler. Closing it needs an `attribute_filter`; deferred to P1
  and documented rather than overclaimed.
- `Window` and `TextField` are not migrated, so `Window`'s four known defects are still
  open. They need `Method`-spec plumbing that lands in P1.

Full list with evidence: `docs/superpowers/P1-BACKLOG.md`.

## Process note

Nine defects were found in the implementation plan **by executing it**, none of which
were visible on reading — including accessors double-wrapping once per inheritance level,
a layering contract that silently enforced nothing (`python -m importlinter.cli lint`
exits 0 without running), and the `python.eval` hole above, which fell exactly between two
tasks that each reasoned correctly about their own half.

The plan document (`docs/superpowers/plans/`) carries a header table recording all nine.
The shipped code and its tests are authoritative.
