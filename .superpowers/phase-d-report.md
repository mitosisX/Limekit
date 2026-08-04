# Phase D report — tier-3 widgets, data, and charts

## Scope delivered

**Widgets** (`limekit/widgets/`):
`Calendar`, `DatePicker`, `TimePicker`, `Knob`, `AdvancedSlider`, `Accordion`,
`GifPlayer`, `SlidingStackedWidget`, `LCDNumber`, `FontComboBox`,
`CommandButton`, `Spacer`, `Separator`.

**Layout**: `StackedLayout` → `limekit/layouts/stackedlayout.py`.

**Data**: `Sqlite3` → `limekit/services/database.py` (`db.Sqlite3`).

**Charts** (`limekit/charts/`, all `chart.<Name>`): `Chart`, `ChartView`,
`LineChart`, `BarChart`, `BarSet`, `AreaChart`, `ValueAxis`, `CategoryAxis`.

**Threading/signals**: `Thread`, `Signal` → `limekit/services/concurrency.py`
(`sys.Thread`, `sys.Signal`).

`Modal` was **not** rebuilt — it already exists at `limekit/widgets/modal.py`
from Phase C. Confirmed before starting rather than assumed.

## QtCharts availability

`PySide6.QtCharts` **imports successfully** in this environment:

```
python -c "import PySide6.QtCharts; print(PySide6.QtCharts.__file__)"
C:\Users\omega\AppData\Local\Programs\Python\Python313\Lib\site-packages\PySide6\QtCharts.pyd
```

Even so, every `limekit/charts/*.py` module imports its Qt base through
`limekit/charts/_qtcharts.py`, which wraps the import in try/except and
exposes `HAS_QTCHARTS`. If `QtCharts` is missing, each chart class still
defines cleanly (falling back to `QObject` as a base so Prop declarations
just fail to resolve and are silently skipped, per the kernel's existing
"abstract mixin" behaviour) and raises a `BridgeError` the moment it is
*instantiated*, via a `require_charts()` guard at the top of every
`__init__`. Collection/import of the rest of the package is never at risk.
`tests/charts/test_charts.py` is marked
`skipif(not HAS_QTCHARTS, reason=...)` for portability to a build that lacks
the add-on, even though it is not skipped here.

## 1.x defects found and NOT reproduced

- **`gui/threading.py:21`**: `def sleep(self): self.sleep()` — unconditional
  infinite recursion (a `RecursionError`/hang on every call, forever). The
  2.0 `Thread.sleep(seconds)` calls the real `QThread.sleep(seconds)`
  static method instead.
- **`components/widgets/lcdnumber.py`**: `setValuee` (misspelled) had a body
  of a bare `self.set` — not even a call, so it always raised
  `AttributeError` if ever reached, and nothing called the misspelled name
  anyway. Replaced with a real `setValue`/`getValue` pair backed by Qt's
  `display()`/`value()`.
- **`components/widgets/pickers/timepicker.py`**: `setDate(self, year,
  month, day): self.setDateTime(QDate(year, month, day))` fed a `QDate`
  (no time component) into `QTimeEdit.setDateTime`, which needs a
  `QDateTime`, on a widget that only ever holds a time — never worked.
  Replaced with `setTime(hour, minute, second)` against `QTime`, which is
  what a `QTimeEdit` actually stores.
- **`components/widgets/pickers/datepicker.py`**: `QDateTime(year, month,
  day, hour, minutes)` — a 5-int-argument overload PySide's `QDateTime`
  does not have — raised a raw `TypeError` on every call. Rebuilding a
  proper `QDateTime(QDate, QTime)` and calling `setDateTime()` with it
  turned out to have its *own* problem: verified against this PySide6/Qt
  build, `QDateEdit.setDateTime()` silently rolls the displayed date back
  one day for a plain local-time midnight `QDateTime` (reproduced directly
  against a bare `QDateEdit`, nothing Limekit-specific). Since `QDateEdit`
  only ever displays a date, never a time, `setDate(year, month, day)` now
  goes through the real Qt native `setDate(QDate)` instead, sidestepping
  the `QDateTime` round-trip bug entirely; the `hour`/`minutes` parameters
  1.x accepted (and never actually displayed) are dropped.
- **`components/layouts/stackedlayout.py`**: `addLayout` called
  `self.addChildLayout(layout)` — `QStackedLayout` has no such method, so
  this branch was dead and unreachable. Replaced with the same
  wrap-in-a-plain-`QWidget` trick `SlidingStackedWidget.addLayout` and
  `Accordion.addLayout` already use.
- **`components/widgets/slidingstackedwidget.py`**: `setAnimation` looked
  up `getattr(QEasingCurve.Type, animation)` and silently swallowed
  `AttributeError` on an unknown curve name — `slider:setAnimation("bogus")`
  did nothing, with no error anywhere. Now raises `BridgeError`.
  `setCurrentWidget` also passed a raw 0-indexed `indexOf(widget)` into
  `setCurrentIndex`, which treats its argument as 1-indexed — an off-by-one
  — now corrected by passing `indexOf(widget) + 1`.
- **`components/charts/chart.py` (2.0's `AreaChart`, née `AreaChart` in
  1.x's `area/areachart.py`)**: `AreaChart.__init__` called
  `QAreaSeries(title)` — `QAreaSeries` has no string-taking constructor
  overload (only `()`, `(upper)`, `(upper, lower)`); this would raise a
  `TypeError` from PySide the instant any Lua script constructed one.
  `append`, which the 1.x class also declared, does not exist on
  `QAreaSeries` at all (confirmed: `hasattr(QAreaSeries, "append")` is
  `False`) — only `QLineSeries` has it, so that method was unreachable
  by construction. Rebuilt to take the upper/lower `LineChart` series
  `QAreaSeries` actually wants, exposing only the real Qt surface (`name`).
- **`components/charts/linegraph/linechart.py`**: `setData` iterated the
  given points and `print(x, " ", y)`-ed them instead of ever calling
  `append` — passing data to `setData` silently drew nothing. `setData`
  now actually appends each point.
- **`core/database/sqlite3.py`**: `get_table_info`, `fetch_tables`, and
  `fetchone` had no try/except around their `sqlite3` calls at all, so a
  raw `sqlite3.Error` could reach a Lua caller directly. Every method in
  the 2.0 `db.Sqlite3` wraps `sqlite3.Error` into `BridgeError`.
  `__enter__`/`__exit__` (Python `with`-statement support) are dropped —
  Lua has no `with` statement, so 1.x's versions were unreachable dead code.

## Design notes / non-obvious decisions

- `AdvancedSlider`'s custom paint/mouse/keyboard internals are kept as-is
  (they *are* the widget); every public getter/setter was ported 1:1,
  colours go through the shared `Colour` coercion, `setBackgroundColor`
  intentionally overrides `LimeWidget.setBackgroundColor` because this
  widget paints its own background rather than using a stylesheet.
- `Accordion.currentIndex` is a `Prop` (its generated `getCurrentIndex`/
  `setCurrentIndex` intentionally shadow the real `QToolBox` methods of the
  same name, matching how `Button.text`/`setText` shadows `QPushButton`);
  `Tab`, `StackedLayout`, `SlidingStackedWidget`, `FontComboBox.currentIndex`
  are hand-written instead because their real Qt index is 0-based and needs
  `LuaIndex` translation, which a `Prop` cannot express.
- `FontComboBox.setFont(string)` and `AdvancedSlider.setFont(QFont)`
  deliberately override the real `QWidget.setFont`, the same shape as
  `TextField.setText` overriding `QTextEdit.setText` — not via `Prop`
  (which the collision guard would refuse), but as plain hand-written
  methods, which the guard never sees.
- `Spacer` wraps `QSpacerItem` (not a `QWidget`) and so does not use the
  `LimeWidget` mixin — the same reasoning that keeps `LimeAction` and
  `LimeLayout` separate from it.
- `Sqlite3`/`Thread`/`Signal` deliberately do **not** import from
  `limekit.widgets` even where a shared helper (`_to_int`) would be
  convenient — `services/` staying independent of `widgets/` is part of the
  existing layering intent, so `concurrency.py` carries its own copy of
  `_to_int` rather than reaching across.
- `limekit.charts` was added to `.importlinter`'s kernel contract
  `forbidden_modules`, alongside `limekit.toolkit` and `limekit.services`.

## Artifacts regenerated

`tools/generate_manifest.py`, `generate_lua.py`, `generate_stubs.py` were
all re-run; a second run afterwards produced an identical `manifest.py`
(diffed byte-for-byte) and `git status --short` showed no further changes
from the second pass — regeneration is a verified no-op.

## Tests

- `tests/widgets/test_tier3_widgets.py` — construction, 1-indexing, guarded
  events, and defect-regression coverage for every tier-3 widget.
- `tests/services/test_database.py` — a real round-trip against a
  `tmp_path` file (write, close, reopen, re-read, to prove persistence
  rather than just in-connection state), plus failure paths asserting
  `BridgeError` for malformed SQL, an invalid path, and empty
  column/value mappings.
- `tests/services/test_concurrency.py` — `Thread`/`Signal` guarded-callback
  coverage, plus a regression test for the sleep() fix.
- `tests/charts/test_charts.py` — `skipif(not HAS_QTCHARTS, ...)` guarded;
  runs for real in this environment.

## Test suite

Baseline: 333 passed / 52 xfailed.
After Phase D: **384 passed / 52 xfailed** (0 failed, 0 new xfails) —
+51 net new passing tests, no regressions.

## Not built / deferred

Nothing in the requested scope was skipped. The `Method` spec type
mentioned in `kernel/declarative.py`'s comments remains out of scope (it
was already out of scope before this phase, per that file's own note).
