# P1 Backlog — carried forward from P0

Everything P0 deliberately deferred, with the evidence that produced it. Sources: 17
task reviews, 6 fix rounds, one whole-branch review and its fix wave.

---

## Blocking for P1 (things P0 promised P1 would do)

**Migrate the 52 demo projects.** `tests/test_demo_smoke.py` xfails every one. They all
use the 1.x flat-global API (`Window{...}`, `VLayout()`). The xfail count *is* this
backlog item's size. Requires the `limekit migrate` codemod named in spec §5, which does
not exist.

**Migrate `Window` and close its four defects.** Excluded from P0's pilot set because its
hand-written event overrides need `Method`-spec plumbing:
- `components/widgets/window.py:291` — `onContextMenuEvent` read but never declared → `AttributeError` unless `setOnContextMenu` was called
- `:230` — `showEvent` calls `center()` on *every* show; the `just_shown` guard is declared and never used
- `:240` — `closeEvent` never calls `super()`, never accepts or ignores
- Plus `TextField`, needed alongside `Window` before the calculator demo can migrate

**Retire the legacy trees.** `limekit/engine/`, `components/`, `core/`, `utils/`, `gui/`
still exist and still import — deliberately, so 1.x apps keep running through P0. When
they go, `GlobalEngine` (8 references in `app_engine.py` and `utils/converters.py`) goes
with them, and the five namespace-package entries in `.importlinter` become genuinely
enforceable. Also delete the stale `limekit/lua/limekit.lua`.

**`gui/threading.py:21`** — `def sleep(self): self.sleep()`, unconditional infinite
recursion. P3 (concurrency) territory.

---

## Security hardening

**`python.as_attrgetter` is an open escape hatch.** P0 closed `python.eval` and
`python.builtins` (`register_eval=False, register_builtins=False`), but lupa always
installs `as_attrgetter`, and it can reach a widget's Qt signal to attach a handler that
bypasses `guard.py`:

```lua
python.as_attrgetter(python.as_attrgetter(b).clicked).connect(function() error("BOOM") end)
```

Spec §7 item 5 was corrected to claim only "no unguarded path **through the generated
accessors**". Closing it properly needs an `attribute_filter` on the `LuaRuntime` — a
design change with real breakage risk, hence deferred.

**Schedule a deliberate adversarial pass over the Lua↔Python boundary as a task**, not as
a review byproduct. P0's Critical finding existed because Task 10 correctly verified lupa
injects no *bare-name* builtins and Task 17 correctly hardened the AST sandbox — and the
hole fell exactly between the two premises. Both tasks passed their reviews.

**`evalExpression("-"*100000 + "1")` leaks a raw `MemoryError`** from `ast.parse`, which
is guarded for `SyntaxError`/`RecursionError` only. Fix with an input-length cap before
parsing.

---

## Known gaps in the collision guard

`declarative._safe_setattr` refuses to overwrite a non-generated attribute, but two cases
still pass silently:

- A hand-written method whose name equals the prop's *own* Qt getter/setter name is
  resolved into `allow` and wrapped rather than refused. Verified benign today (bound at
  generation time, no recursion), but it is a silent wrap.
- Two Props generating the *same* accessor name clobber each other — generated-vs-generated
  passes the `_lime_generated` check.

Related latent trap: **`ComboBox.getText`** (`limekit/widgets/combobox.py`) is a
hand-written method with a generated accessor's name. It survives only because `ComboBox`
declares no `text` Prop. The moment P1 hoists `text` onto a shared base — likely, since 3
of 5 widgets declare it — the guard will fire at class-definition time. That is the
intended behaviour, but expect it.

---

## Infrastructure

**There is no CI.** No `.github/` at all. Every "verified in CI" claim in spec §7 is an
uninvoked local test — including the three regeneration no-op checks that exist
specifically to catch stale generated artifacts. A ~15-line workflow running `pytest`,
`lint-imports` and the three generators makes those claims true as written.

**`tools/generate_stubs.py` diverges from its two siblings.** No `--stdout`, so its no-op
test writes into the working tree (dirtying the repo on failure), and it never prunes
orphaned `stubs/*.lua` — delete a module and the stale file survives with `before == after`
still true.

**Generator ordering is undocumented.** Adding a widget requires running three commands in
a specific order (manifest first; the other two read it). Nothing says so.

**`tests/test_demo_smoke.py` resolves demos from a path outside the repo** at collection
time. The "52 xfailed" is a local artifact; elsewhere the suite collects one skip.

---

## Deferred minors (ruled non-blocking by the whole-branch review)

| Area | Item |
|---|---|
| `guard.py` | `WidgetCallbackError` is never raised, so its own `__traceback__` is `None`; the cause chain still prints |
| `convert.py` | `to_lua` on a Python `set` uses nondeterministic iteration order — sort it or drop `set` |
| `convert.py` | `as_sequence` on a Lua *map* returns values in dict order — undefined for `setItems{a="x", b="y"}` |
| `coerce.py` | Lua callers cannot combine alignment flags via string (`"left|top"` raises cleanly); needs a bitmask-aware `Enum` |
| `text.py` | Pow digit estimate undercounts by 1 at exact powers of ten (`10**1000` → 1001 digits against a nominal 1000 ceiling); cosmetic |
| `app.py` | `setHighDpiScaleFactorRoundingPolicy` called unconditionally in `boot()`, emitting a benign Qt warning when an app already exists |
| `registry.py` | No test for deep-path grouping (`ui.forms.Button`) or same-class re-registration |
| `generate_manifest.py` | `discover()` unconditionally skips `__init__.py`; a `__lime__` class defined there is silently omitted — should raise instead |
| `test_layering.py` | Grep test does substring matching; a relative import (`from ...engine.parts import X`) inside `kernel/` would not be caught |
| `spec.py` | `sys.Expr.evalExpression` vs the spec's `sys.evalExpression` — settle the naming before P1 codifies it |
| widgets | No tests for `Label.textAlignment` bitmask round-trip or `Button.icon` getter type |
| deps | Dependency-import test covers 5 of 9 declared runtime deps |

---

## Removed in P0, reintroduce only with a consumer

`Prop.default`, `Method`, and `Event.args` were deleted from the public spec surface. All
three were declared, documented, and read by nothing — the exact anti-pattern spec §1.1
indicts 1.x's `settings.IGNORE_PARTS` for. `default` was duplicated in every widget's
`__init__` anyway. Reintroduce them when something actually consumes them, not before.
