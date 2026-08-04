# Phase C report -- tier-2 structural widgets

## What was built

All eight groups from the plan, in `limekit/widgets/`:

- `tab.py` -- `Tab`, `TabItem`
- `menu.py` -- `Menu`, `MenuItem`, `Menubar`, `DropMenu`
- `toolbar.py` -- `Toolbar`, `ToolbarButton`
- `dock.py` -- `Dock`
- `table.py` -- `Table`, `TableItem`
- `treeview.py` -- `TreeView`, `TreeViewItem`
- `statusbar.py` -- `StatusBar`
- `modal.py` -- `Modal`

Plus `action_base.py`, a new `LimeAction` mixin (parallel to `LimeWidget`
and `LimeLayout`) for the two classes that wrap `QAction` (a `QObject`, not
a `QWidget`): `MenuItem` and `ToolbarButton`.

All three generated artifacts were regenerated (`generate_manifest.py`,
`generate_lua.py`, `generate_stubs.py`) and a second run of all three
produced no further diff (idempotent, as CI requires). `git status --short`
is clean after committing. Full suite: 317 passed / 52 xfailed before this
work, **333 passed / 52 xfailed** after (16 new tests in
`tests/widgets/test_tier2_widgets.py`, one per widget group plus a
registration test).

## TreeView: which 1.x source was taken, and why

1.x had two incompatible implementations:

- `components/widgets/tree_widget.py` -- a `QTreeWidget` subclass
  (`TreeWidget`) with a companion `TreeItem` wrapper class. Complete,
  internally consistent, and correct.
- `components/widgets/treewidget.py` -- a `QTreeView` subclass (also named
  `TreeView`, confusingly) built on `QStandardItemModel`. Explicitly marked
  `"Half baked"` in its own comments, and genuinely broken:
  `setTreeItemExpanded` called `self.model(x, y)` as though the model
  object were callable (it isn't -- that's a guaranteed `TypeError` at
  runtime), and `setHeaders` piped a raw Lua table straight into
  `setHorizontalHeaderLabels` with no coercion.

I took `tree_widget.py`'s `QTreeWidget` design and exposed it under the
requested names (`TreeView`, `TreeViewItem`), and did not port anything
from `treewidget.py`. Reconciling two different object models (item-based
vs. model-based) into one class would have meant inventing behaviour no
1.x code actually exercised; `QTreeWidget` is also the same family as the
already-shipped tier-1 `ListBox` (`QListWidget`) and tier-2 `Table`
(`QTableWidget`), so it keeps the item-widget style consistent across the
whole widget set.

## Collisions the guard caught (worked as designed)

- **`Table`**: a naive `rowCount`/`columnCount` Prop generates
  `getRowCount`/`setRowCount`, which happen to be the literal Qt method
  names -- allowed as an "intentional shadow" by the guard. But `Table`
  also needs a hand-written `setRowCount` that runs its argument through
  `_to_int` for a Limekit-flavoured `BridgeError` instead of a raw
  `TypeError`; combined with the Prop, that second definition collided.
  Resolved by hand-writing `setRowCount`/`getRowCount`/`setColumnCount`/
  `getColumnCount` directly and not declaring them as Props at all.
- **`Table`**: a Prop meant to expose "the current item", naively named
  `item`, generates `setItem` -- shadowing `QTableWidget.setItem(row,
  column, item)`, a real, differently-shaped (3-argument) method it was
  never meant to wrap. Resolved by never declaring an `item` Prop; cell
  access is entirely hand-written (`getCellItem`, `getCurrentItem`, etc.),
  matching the reasoning that every row/column accessor needs `LuaIndex`
  translation anyway, which a Prop cannot do.
- **`Tab`**: same shape of trap on `setCurrentIndex` -- `QTabWidget`'s real
  `setCurrentIndex`/`currentIndex` are 0-indexed, so a `currentIndex` Prop
  would either need to skip index translation (wrong) or collide with a
  hand-written 1-indexed override (guard fires). Resolved the same way:
  no `currentIndex` Prop, a hand-written `setCurrentIndex`/`getCurrentIndex`
  pair instead, following the same pattern `ListBox` already established
  for `getCurrentRow`/`setCurrentRow`.

No prop names were renamed as aliases this time (unlike `TextField.plainText`)
-- in every tier-2 case the cleaner fix was "don't make it a Prop, hand-write
it," because the underlying operation needed index translation a Prop
cannot express, not because the accessor name itself needed renaming.

## 1.x defects found and deliberately not reproduced

- **`Modal.show()` called `self.exec()`** -- Qt's *blocking* modal event
  loop -- so `modal:show()` meant something completely different from
  every other widget's `show()`, and would hang dead in a headless test
  (or any non-interactive context). Not reproduced: `Modal` inherits
  `LimeWidget.show()` (non-blocking) unchanged, and blocking modal
  behaviour is available explicitly via a new `open()` method.
- **`ToolbarButton.isChecked` called `super().isChecked()()`** -- an extra,
  erroneous pair of parentheses. `isChecked()` returns a `bool`, and
  calling a `bool` raises `TypeError: 'bool' object is not callable` the
  moment any Lua code invoked it. Replaced by `LimeAction.checked`, a
  working generated Prop.
- **`Menu`/`Menubar` `buildFromTemplate`/`fromTemplate`/`buildFromTemplate__`**
  -- each class carried two or three separate, mutually inconsistent
  attempts at building a menu tree from a Lua table (disagreeing on
  whether `"submenu"` nests under `item.submenu` or `item["submenu"]`,
  one of them dead code with a comment admitting "total waste of time"),
  plus a shared **class-level** `objects = {}` dict that leaked every
  named menu item across every `Menu`/`Menubar` instance ever constructed
  in the process, since it was never made an instance attribute. None of
  this is reproduced. Building a menu tree from Lua is just
  `addMenuItem`/`addMenu` calls, which is what all three templating
  attempts bottomed out in anyway.
- **`Dock.setMagneticAreas`** silently ignored unrecognised area strings
  (an `if/elif` chain with no `else`). The replacement, `setAllowedAreas`,
  raises `BridgeError` on an unknown area name instead of dropping it,
  matching how every other Enum-backed coercion in the kernel behaves.
- **`Table.getColumnsCount`/`getRowsCount`/`setColumnHeaderToolTip`-adjacent
  methods used bare 0-indexed positions inconsistently** with the rest of
  the framework's Lua-facing surface (1.x's own `Table` mixed 0-indexed
  `row`/`column` params in most methods with a stray `+1` in exactly one
  place, `getIndexOf`-equivalents elsewhere). Every row/column/index
  parameter in the new `Table`/`Tab`/`TreeView`/`Dock` is uniformly
  1-indexed via `LuaIndex`, with no exceptions.

## Notes

- `DropMenu` is a plain subclass of `Menu` with no added members: 1.x kept
  it as a near-duplicate file (its own `addDropMenu`/`addMenuItem` aliases,
  its own `setImage`), but nothing in it wasn't already covered by `Menu`'s
  `icon` Prop and `addMenuItem`/`addMenu`. Kept as a subclass rather than
  a second copy.
- Everything imports cleanly through `manifest.import_all()` with zero
  `RegistryError`s at collection time -- the collisions above were caught
  and fixed during development, not left as known-broken.
