"""Event index translation in the generated `setOn<Name>` attachers.

Qt counts positions from 0; every Lua-facing index in Limekit counts from 1.
Props and methods went through `LuaIndex` and got this right, but events
handed the signal's arguments straight through, so `Table.onCellClick`
reported the top-left cell as `(0, 0)` while `setCellText(1, 1)` addressed it.

`Tab` had already worked around this by hand-writing its attacher and adding
`index + 1` -- its module docstring says translating "needs a real wrapper,
not a raw connect". Declaring `indices=` on the Event gets every widget the
same treatment.
"""

import pytest

from limekit.kernel.bridge.guard import reset_error_sink, set_error_sink
from limekit.kernel.spec import Event


@pytest.fixture(autouse=True)
def sink():
    captured = []
    set_error_sink(captured.append)
    yield captured
    reset_error_sink()


# -- the spec ----------------------------------------------------------------

def test_index_positions_maps_names_to_argument_offsets():
    event = Event("cellClicked",
                  params=(("row", "integer"), ("column", "integer")),
                  indices=("row", "column"))
    event.name = "onCellClick"
    assert event.index_positions() == (0, 1)


def test_index_positions_picks_out_only_the_marked_ones():
    """TreeView.onItemClick delivers (item, column); only column is a position."""
    event = Event("itemClicked",
                  params=(("item", "any"), ("column", "integer")),
                  indices=("column",))
    event.name = "onItemClick"
    assert event.index_positions() == (1,)


def test_no_indices_means_no_translation():
    event = Event("valueChanged", params=(("value", "integer"),))
    event.name = "onValueChange"
    assert event.index_positions() == ()


# -- the generated attacher --------------------------------------------------

def test_table_cell_event_is_one_based(qapp):
    from limekit.widgets.table import Table

    table = Table(3, 2)
    table.setCellText(1, 1, "top-left")

    seen = []
    table.setOnCellClick(lambda sender, row, column: seen.append((row, column)))

    table.cellClicked.emit(0, 0)          # Qt's top-left
    assert seen == [(1, 1)]

    # and the reported position addresses the cell the user actually clicked
    row, column = seen[0]
    assert table.getCellItem(row, column).getText() == "top-left"


def test_combobox_index_event_is_one_based(qapp):
    from limekit.widgets.combobox import ComboBox

    combo = ComboBox(["a", "b", "c"])
    seen = []
    combo.setOnItemSelect(lambda sender, index: seen.append(index))

    combo.setCurrentIndex(2)              # Qt's third item
    assert seen[-1] == 3
    assert combo.getItemAt(seen[-1]) == "c"


def test_no_selection_reports_zero(qapp):
    """Qt says -1 for "nothing selected"; in 1-based counting that is 0."""
    from limekit.widgets.combobox import ComboBox

    combo = ComboBox(["a", "b"])
    seen = []
    combo.setOnItemSelect(lambda sender, index: seen.append(index))

    combo.setCurrentIndex(-1)
    assert seen[-1] == 0

    # 0 is already rejected everywhere else as out of range, so a handler that
    # forwards it into an index-taking method gets a real error rather than
    # the wrong item.
    from limekit.kernel.errors import BridgeError
    with pytest.raises(BridgeError):
        combo.getItemAt(0)


def test_treeview_translates_only_the_column(qapp):
    from limekit.widgets.treeview import TreeView, TreeViewItem

    tree = TreeView()
    tree.setHeaderLabels(["Name", "Size"])
    item = TreeViewItem(["report.pdf", "2 MB"])
    tree.addTopItem(item)

    seen = []
    tree.setOnItemClick(lambda sender, clicked, column: seen.append((clicked, column)))

    tree.itemClicked.emit(item, 1)        # Qt's second column
    assert len(seen) == 1
    clicked, column = seen[0]
    assert column == 2                    # translated
    assert clicked is item                # left alone
    assert clicked.getText(column) == "2 MB"


def test_values_are_not_translated(qapp):
    """Only positions shift. A slider's value is a value, not an index."""
    from limekit.widgets.slider import Slider

    slider = Slider()
    slider.setRange(0, 10)
    seen = []
    slider.setOnValueChange(lambda sender, value: seen.append(value))

    slider.setValue(7)
    assert seen[-1] == 7


def test_booleans_are_never_shifted(qapp):
    """bool is an int subclass, so a naive `+ 1` would turn True into 2.

    No shipped event marks a boolean as an index, so this exercises the guard
    directly rather than through a widget that cannot reach it.
    """
    from PySide6.QtCore import QObject
    from PySide6.QtCore import Signal as QtSignal

    from limekit.kernel.declarative import LimeObject

    class Probe(LimeObject, QObject):
        fired = QtSignal(bool, int)
        # Deliberately marks both, including the boolean.
        onFired = Event("fired",
                        params=(("flag", "boolean"), ("position", "integer")),
                        indices=("flag", "position"))

    probe = Probe()
    seen = []
    probe.setOnFired(lambda sender, flag, position: seen.append((flag, position)))

    probe.fired.emit(True, 0)
    probe.fired.emit(False, 4)

    assert seen == [(True, 1), (False, 5)]      # bools untouched, ints shifted


def test_missing_trailing_argument_is_tolerated(qapp):
    """Some Qt signals have overloads that omit a trailing argument.

    `clicked` is emitted both as `clicked(bool)` and `clicked()`, so a shift
    must not assume every declared parameter actually arrived.
    """
    from limekit.widgets.checkbox import CheckBox

    box = CheckBox("x")
    seen = []
    box.setOnCheck(lambda sender, *rest: seen.append(rest))

    box.clicked.emit()                  # the no-argument overload
    assert seen == [()]
