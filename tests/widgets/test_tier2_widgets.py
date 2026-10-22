"""Tier-2 structural widgets: construction, children/items, 1-indexing,
one guarded event per widget.

Mirrors the conventions in test_pilot_widgets.py / test_tier1_widgets.py.
The `qapp` fixture comes from tests/conftest.py; the `sink` fixture
(captures guarded errors instead of printing them) is redeclared here
identically rather than imported across test files, per those files' own
convention.
"""

import pytest

from limekit.kernel.bridge.guard import reset_error_sink, set_error_sink
from limekit.kernel.errors import BridgeError


@pytest.fixture(autouse=True)
def sink():
    captured = []
    set_error_sink(captured.append)
    yield captured
    reset_error_sink()


# -- Tab / TabItem -----------------------------------------------------------

def test_tab_addtab_and_1_indexed_access(qapp):
    from limekit.widgets.tab import Tab, TabItem

    tab = Tab()
    first, second = TabItem(), TabItem()
    assert tab.addTab(first, "First") is tab
    tab.addTab(second, "Second")

    assert tab.getCount() == 2
    assert tab.getChildAt(1) is first
    assert tab.getChildAt(2) is second
    assert tab.getIndexOf(second) == 2

    tab.setCurrentIndex(2)
    assert tab.getCurrentIndex() == 2

    tab.setTabText(1, "Renamed")
    assert tab.getTabText(1) == "Renamed"

    with pytest.raises(BridgeError):
        tab.setCurrentIndex(0)                   # 1-indexed, 0 is out of range


def test_tab_ontabchange_guarded(qapp, sink):
    from limekit.widgets.tab import Tab, TabItem

    tab = Tab()
    tab.addTab(TabItem(), "a")
    tab.addTab(TabItem(), "b")
    tab.setOnTabChange(lambda *a: 1 / 0)
    tab.setCurrentIndex(2)
    assert len(sink) == 1


# -- Menu / MenuItem / Menubar / DropMenu -------------------------------------

def test_menu_additems_and_menubar(qapp):
    from limekit.widgets.menu import DropMenu, Menu, MenuItem, Menubar

    menu = Menu("File")
    item = MenuItem("Open")
    assert menu.addMenuItem(item) is menu
    assert item in menu.actions()

    submenu = Menu("Recent")
    assert menu.addMenu(submenu) is menu

    bar = Menubar()
    assert bar.addMenu(menu) is bar

    drop = DropMenu("Extra")
    drop_item = MenuItem("Choice")
    drop.addMenuItem(drop_item)
    assert drop_item in drop.actions()


def test_menuitem_onclick_guarded(qapp, sink):
    from limekit.widgets.menu import MenuItem

    item = MenuItem("Open")
    item.setOnClick(lambda *a: 1 / 0)
    item.trigger()
    assert len(sink) == 1


# -- Toolbar / ToolbarButton ---------------------------------------------------

def test_toolbar_addbutton_and_props(qapp):
    from limekit.widgets.toolbar import Toolbar, ToolbarButton
    from PySide6.QtCore import Qt

    bar = Toolbar("Main")
    button = ToolbarButton("Save")
    assert bar.addButton(button) is bar
    assert button in bar.actions()

    bar.setToolButtonStyle("icononly")
    assert bar.getToolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly

    button.setCheckable(True)
    button.setChecked(True)
    assert button.isChecked() is True


def test_toolbarbutton_onclick_guarded(qapp, sink):
    from limekit.widgets.toolbar import ToolbarButton

    button = ToolbarButton("Save")
    button.setOnClick(lambda *a: 1 / 0)
    button.trigger()
    assert len(sink) == 1


# -- Dock ----------------------------------------------------------------------

def test_dock_child_and_areas(qapp):
    from limekit.widgets.dock import Dock
    from limekit.widgets.label import Label
    from PySide6.QtCore import Qt

    dock = Dock("Panel")
    label = Label("content")
    assert dock.setChild(label) is dock
    assert dock.getChild() is label

    dock.setAllowedAreas("left", "right")
    assert dock.allowedAreas() == (
        Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
    )

    dock.setFeatures("movable", "closable")

    with pytest.raises(BridgeError):
        dock.setAllowedAreas()


def test_dock_onvisibilitychange_guarded(qapp, sink):
    from limekit.widgets.dock import Dock

    dock = Dock()
    dock.setOnVisibilityChange(lambda *a: 1 / 0)
    dock.visibilityChanged.emit(True)
    assert len(sink) == 1


# -- Table / TableItem -----------------------------------------------------------

def test_table_cells_are_1_indexed(qapp):
    from limekit.widgets.table import Table

    table = Table(2, 2)
    assert table.setColumnHeaders(["A", "B"]) is table
    assert table.getColumnHeaderText(1) == "A"

    table.setCellText(1, 1, "hi")
    item = table.getCellItem(1, 1)
    assert item.getText() == "hi"

    table.setCurrentCell(1, 1)
    assert table.getCurrentRow() == 1
    assert table.getCurrentColumn() == 1

    position = table.addRow()
    assert position == 3
    assert table.getRowCount() == 3

    with pytest.raises(BridgeError):
        table.getCellItem(0, 1)                  # 1-indexed, 0 is out of range


def test_table_oncellclick_guarded(qapp, sink):
    from limekit.widgets.table import Table

    table = Table(2, 2)
    table.setOnCellClick(lambda *a: 1 / 0)
    table.cellClicked.emit(0, 0)
    assert len(sink) == 1


# -- TreeView / TreeViewItem -----------------------------------------------------

def test_treeview_hides_a_column_by_its_1_based_index(qapp):
    from limekit.widgets.treeview import TreeView

    tree = TreeView()
    tree.setHeaderLabels(["widget", "address"])
    assert tree.setColumnHidden(2, True) is tree
    assert tree.isColumnHidden(1) and not tree.isColumnHidden(0)
    tree.setColumnHidden(2, False)
    assert not tree.isColumnHidden(1)


def test_treeview_items_are_1_indexed(qapp):
    from limekit.widgets.treeview import TreeView, TreeViewItem

    tree = TreeView()
    assert tree.setHeaderLabels(["Name", "Value"]) is tree

    root = TreeViewItem(["root", "1"])
    tree.addTopItem(root)
    assert tree.getTopItemCount() == 1
    assert tree.getTopItemAt(1) is root

    child = TreeViewItem(["child"])
    root.addChild(child)
    assert root.getChildCount() == 1
    assert root.getChildAt(1) is child
    assert child.getParent() is root

    child.setText(1, "renamed")
    assert child.getText(1) == "renamed"

    with pytest.raises(BridgeError):
        root.getChildAt(0)                        # 1-indexed, 0 is out of range


def test_treeview_onitemclick_guarded(qapp, sink):
    from limekit.widgets.treeview import TreeView, TreeViewItem

    tree = TreeView()
    root = TreeViewItem(["root"])
    tree.addTopItem(root)
    tree.setOnItemClick(lambda *a: 1 / 0)
    tree.itemClicked.emit(root, 0)
    assert len(sink) == 1


# -- StatusBar -------------------------------------------------------------------

def test_statusbar_text_and_children(qapp):
    from limekit.widgets.statusbar import StatusBar
    from limekit.widgets.label import Label

    bar = StatusBar()
    assert bar.setText("Ready") is bar
    assert bar.currentMessage() == "Ready"

    assert bar.addChild(Label("left")) is bar
    assert bar.addPermanentChild(Label("right")) is bar

    assert bar.clear() is bar
    assert bar.currentMessage() == ""


# -- Modal -------------------------------------------------------------------

def test_modal_props_and_dismiss(qapp):
    from limekit.widgets.modal import Modal
    from limekit.widgets.window import Window

    window = Window()
    modal = Modal("Confirm", window)
    assert modal.getTitle() == "Confirm"
    assert modal.isModal() is True
    assert modal.dismiss() is modal


def test_modal_onshown_guarded(qapp, sink):
    from limekit.widgets.modal import Modal

    modal = Modal("Confirm")
    modal.setOnShown(lambda *a: 1 / 0)
    from PySide6.QtGui import QShowEvent
    modal.showEvent(QShowEvent())
    assert len(sink) == 1


def test_modal_frameless_toggles_the_frame(qapp):
    from PySide6.QtCore import Qt
    from limekit.widgets.modal import Modal

    modal = Modal("Card")
    assert modal.isFrameless() is False
    assert modal.setFrameless(True) is modal
    assert modal.isFrameless() is True
    assert modal.windowFlags() & Qt.WindowType.FramelessWindowHint
    # Opaque: the modal is the surface. A translucent window on Windows 11
    # gets a system border drawn round its transparent margin.
    assert not modal.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    modal.setFrameless(False)
    assert modal.isFrameless() is False


def test_modal_opacity_round_trips(qapp):
    from limekit.widgets.modal import Modal

    modal = Modal("Card")
    assert modal.setOpacity(0.5) is modal
    assert modal.getOpacity() == pytest.approx(0.5, abs=0.01)


def test_modal_fade_in_shows_and_reaches_full_opacity(qapp, qtbot):
    from limekit.widgets.modal import Modal

    modal = Modal("Card")
    assert modal.fadeIn(60) is modal
    assert modal.isVisible()
    qtbot.waitUntil(lambda: modal.getOpacity() > 0.99, timeout=2000)


def test_modal_fade_out_closes_and_fires_onclose_once(qapp, qtbot):
    from limekit.widgets.modal import Modal

    closed = []
    modal = Modal("Card")
    modal.setOnClose(lambda *a: closed.append(True))
    modal.fadeIn(1)
    assert modal.fadeOut(60) is modal
    modal.fadeOut(60)  # a second dismissal while fading is ignored
    qtbot.waitUntil(lambda: not modal.isVisible(), timeout=2000)
    assert closed == [True]


def test_modal_onmousepress_reports_position_and_is_guarded(qapp, sink):
    from PySide6.QtCore import QEvent, QPointF, Qt
    from PySide6.QtGui import QMouseEvent
    from limekit.widgets.modal import Modal

    seen = []
    modal = Modal("Card")
    assert modal.setOnMousePress(lambda m, x, y: seen.append((m, x, y))) is modal
    press = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(12, 34), QPointF(12, 34),
                        Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
                        Qt.KeyboardModifier.NoModifier)
    modal.mousePressEvent(press)
    assert seen == [(modal, 12, 34)]

    modal.setOnMousePress(lambda *a: 1 / 0)
    modal.mousePressEvent(press)
    assert len(sink) == 1


# -- Registration --------------------------------------------------------------

def test_tier2_widgets_are_registered(qapp):
    from limekit.kernel.registry import registry
    import limekit.widgets.tab, limekit.widgets.menu               # noqa: F401
    import limekit.widgets.toolbar, limekit.widgets.dock            # noqa: F401
    import limekit.widgets.table, limekit.widgets.treeview          # noqa: F401
    import limekit.widgets.statusbar, limekit.widgets.modal         # noqa: F401

    for path in (
        "ui.Tab", "ui.TabItem", "ui.Menu", "ui.MenuItem", "ui.Menubar",
        "ui.DropMenu", "ui.Toolbar", "ui.ToolbarButton", "ui.Dock",
        "ui.Table", "ui.TableItem", "ui.TreeView", "ui.TreeViewItem",
        "ui.StatusBar", "ui.Modal",
    ):
        assert registry.get(path) is not None
