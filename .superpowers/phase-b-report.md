# Phase B report - tier-1 widgets

## Built (13 classes, 12 files + FormLayout)

| Class | File | Notes |
|---|---|---|
| `LineEdit` | `limekit/widgets/lineedit.py` | `text` is a plain Prop (unlike TextField's `plainText` workaround - QLineEdit.setText never guesses HTML). `inputMode` is a Prop wrapping `echoMode`/`setEchoMode` with an Enum coerce, keeping the 1.x-facing name while being declarative. |
| `GroupBox` | `limekit/widgets/groupbox.py` | `layout` is a Prop (`layout`/`setLayout` is a real Qt getter/setter pair). |
| `FormLayout` | `limekit/layouts/formlayout.py` | `addChild(title, child=None)` mirrors `QFormLayout.addRow`'s two call shapes (labelled row vs. bare widget). Added `getRowAt(index)`, 1-indexed via `LuaIndex`, since 1.x's `getAt` did raw `index - 1` on `takeAt` (which *removes* the row) rather than reading it. |
| `Container` | `limekit/widgets/container.py` | `layout` is a Prop. `onKeyPress` overrides a Qt virtual method (not a signal), so it's hand-written like `Window`'s events, but still guarded. |
| `Image` | `limekit/widgets/image.py` | Dropped `resizeImage`, a byte-for-byte duplicate of `setImageSize` in 1.x. `setImageSize` now raises `BridgeError` if called before `setImage` (1.x would `AttributeError` on `NoneType.scaled`). |
| `Spinner` | `limekit/widgets/spinner.py` | `value`/`prefix`/`suffix` are Props. `setRange` stays hand-written (two-arg, no matching single getter). |
| `DoubleSpinner` | `limekit/widgets/doublespinner.py` | Same shape as Spinner, `value` is `float`. |
| `ProgressBar` | `limekit/widgets/progressbar.py` | `value`/`orientation` are Props (`orientation`/`setOrientation` is a real Qt pair, shared `ORIENTATIONS` enum from `kernel/coerce.py`). |
| `Slider` | `limekit/widgets/slider.py` | `value`/`orientation`/`tickPosition` are Props. |
| `RadioButton` | `limekit/widgets/radiobutton.py` | `text`/`checked`/`icon`/`iconSize` are Props; `iconSize` reuses the existing `Size` coerce (`{width, height}` pair) instead of a hand-written two-arg method. |
| `HLine` / `VLine` | `limekit/widgets/horizontal_line.py`, `vertical_line.py` | Thin `QFrame` constructors, no distinguishing surface. |
| `Splitter` | `limekit/widgets/splitter.py` | `handleWidth`/`orientation`/`sizes` are Props (`sizes`/`setSizes` is a real pair; coerces a Lua table/Python list to `list[int]`). `addChild`/`addLayout` stay hand-written (no matching getter). |
| `Scroller` | `limekit/widgets/scroller.py` | `resizable` is a Prop. `onScroll` connects to `verticalScrollBar().valueChanged`, a signal on a child object, so it can't use the declarative `Event` spec (which resolves the signal on `self`) - hand-written but guarded. `setChild` now also updates the internal `_central` reference so a later `setLayout` doesn't silently target the widget's old child (1.x left `parent_widget` stale after `setChild`). |
| `ButtonGroup` | `limekit/widgets/buttongroup.py` | Uses `LimeObject` directly, not `LimeWidget` - `QButtonGroup` is a `QObject`, not a `QWidget`, so the widget-only props (`enabled`, `visible`, ...) don't apply. `exclusive` is a Prop; `onClick` is a declarative `Event` on `buttonClicked`. |

Also added a shared `ORIENTATIONS` enum table to `limekit/kernel/coerce.py` (used by `ProgressBar`, `Slider`, `Splitter`), following the same "one shared table per Qt enum" pattern as `ALIGNMENTS`/`CURSORS`.

## 1.x defects found and *not* reproduced

- **`Image.resizeImage` / `Image.setImageSize`** were identical methods (copy-paste duplication) - only `setImageSize` survives.
- **`Image.setImageSize`** crashed with a raw `AttributeError` (`NoneType.scaled`) if called before `setImage`; now raises `BridgeError`.
- **`FormLayout.getAt`** called `takeAt(index - 1)`, which *removes* the item from the layout as a side effect of "reading" it - a destructive getter. Replaced with `getRowAt`, which reads via `itemAt` (non-destructive) and is properly 1-indexed through `LuaIndex` rather than raw `- 1`.
- **`Scroller.setResizable`** was declared twice in 1.x (harmless but pointless); now a single generated Prop accessor.
- **`Scroller.setChild`** didn't update the `parent_widget` reference used internally by `setLayout`, so calling `setChild` then `setLayout` would silently affect the old widget. Fixed by having `setChild` update `_central` too. (`setChild` and `setLayout` remain two different ways to populate the Scroller, matching 1.x's intent - just no longer able to desync.)
- **`LineEdit.setCursor`**'s cursor map in 1.x mapped `"wait"` to `Qt.CursorShape.ArrowCursor` (should be `WaitCursor`) and listed `"openhand"` twice, with the second definition (`CustomCursor`) silently winning. Reused the already-corrected shared `CURSORS` table from `kernel/coerce.py` (the same fix already applied to `Label` in an earlier phase) instead of re-introducing the bug.

## Declarative-vs-hand-written judgment calls

Per the "declare, don't hand-write" rule, several props that 1.x implemented as thin hand-written wrappers around a genuine Qt getter/setter pair were converted to `Prop`s instead: `LineEdit.inputMode` (`echoMode`/`setEchoMode`), `GroupBox.layout` / `Container.layout` (`layout`/`setLayout`), `RadioButton.iconSize` (`iconSize`/`setIconSize`, reusing the `Size` coerce), `ProgressBar`/`Slider`/`Splitter.orientation` (`orientation`/`setOrientation`, new shared `ORIENTATIONS` enum), `Slider.tickPosition`, and `Splitter.sizes`. Two-argument setters with no matching single-value getter (`setRange` on `Spinner`/`DoubleSpinner`/`ProgressBar`/`Slider`, `addChild`/`addLayout` on `Splitter`/`FormLayout`) stay hand-written, consistent with `BoxLayout.addChild` in the existing codebase.

## Test coverage

`tests/widgets/test_tier1_widgets.py` - 26 tests: construction, prop round-trips (including coercion, e.g. `LineEdit.setText(42)`), one guarded event per widget verified through the `sink` fixture, 1-indexing on `FormLayout.getRowAt` (including a `BridgeError` on `getRowAt(0)`), `RadioButton`/`ButtonGroup` mutual-exclusion behaviour, and a registration check for all 15 new `__lime__` paths.

## Verification

- `python tools/generate_manifest.py && python tools/generate_lua.py && python tools/generate_stubs.py` - re-run twice; second run is byte-identical to the first (verified no-op regeneration).
- `git status --short` after generation: only expected new/modified files (13 new widget/layout modules, 1 new test file, `kernel/coerce.py`, and the three generated artifacts).
- Full suite: **291 passed / 52 xfailed → 317 passed / 52 xfailed** (26 new tests, zero regressions).

## Not built / out of scope

- Generic width/height convenience methods present on several 1.x widgets (`setMinWidth`, `setMaxWidth`, `setFixedWidth`, etc. on `LineEdit`) were not ported: `LimeWidget` already provides `setSize`/`setFixedSize`/`setResizeRule`, and these per-widget duplicates weren't part of any existing shared mixin to declare against. Left as a P1 candidate for a shared `setMinSize`/`setMaxSize` pair on `LimeWidget` if examples need it.
- `Table`, `TreeWidget`, `Accordion`, and the other `components/` widgets not in the tier-1 list were left untouched, as scoped.
