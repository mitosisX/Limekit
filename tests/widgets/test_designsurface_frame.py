"""The surface's chrome: the overlay the selection is drawn on, the mock
window frame around the design, and the small additions a designer needs
from Table, TreeView and WidgetPalette."""

import pytest
from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from limekit.kernel import manifest


@pytest.fixture(scope="module", autouse=True)
def qapp():
    manifest.import_all()
    return QApplication.instance() or QApplication([])


@pytest.fixture
def design(qapp):
    from limekit.layouts.vlayout import VLayout
    from limekit.widgets.button import Button
    from limekit.widgets.container import Container
    from limekit.widgets.designsurface import DesignSurface
    from limekit.widgets.lineedit import LineEdit

    surface = DesignSurface()
    surface.resize(500, 400)

    box, layout = Container(), VLayout()
    edit, button = LineEdit(), Button("press")
    layout.addChild(edit)
    layout.addChild(button)
    box.setLayout(layout)
    box.setFixedSize(200, 120)

    surface.setDesignChild(box)
    surface.show()
    QApplication.processEvents()
    return {"surface": surface, "box": box, "edit": edit, "button": button}


def press(surface, point):
    event = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(point),
                        Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
                        Qt.KeyboardModifier.NoModifier)
    surface.mousePressEvent(event)


def centre_of(widget, surface):
    return widget.mapTo(surface, widget.rect().center())


def test_the_overlay_is_above_the_design(design):
    """Drawn after the design, so an opaque widget cannot hide its own
    selection outline -- the reason the overlay exists."""
    surface = design["surface"]
    siblings = [c for c in surface.children() if c is surface._overlay or c is design["box"]]
    assert siblings[-1] is surface._overlay
    assert surface._overlay.geometry() == surface.rect()


def test_the_overlay_never_catches_a_click(design):
    surface = design["surface"]
    assert surface._overlay.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    selected = []
    surface.setOnSelect(lambda widget: selected.append(widget))
    press(surface, centre_of(design["edit"], surface))
    assert selected == [design["edit"]]


def test_the_design_is_centred_with_room_for_a_title_bar(design):
    surface, box = design["surface"], design["box"]
    title = surface._title_rect()
    assert title.bottom() < box.geometry().top() + 1
    assert title.top() >= 0
    assert abs(box.geometry().center().x() - surface.rect().center().x()) <= 1


def test_clicking_the_title_bar_selects_the_window(design):
    surface = design["surface"]
    selected = []
    surface.setOnSelect(lambda widget: selected.append(widget))
    press(surface, surface._title_rect().center())
    assert selected == [design["box"]]


def test_clicking_the_backdrop_selects_nothing(design):
    surface = design["surface"]
    selected = []
    surface.setOnSelect(lambda widget: selected.append(widget))
    press(surface, QPoint(3, 3))
    assert selected == [None]


def test_frame_title_and_empty_hint_are_settable(design):
    surface = design["surface"]
    assert surface.setFrameTitle("Login") is surface
    assert surface._frameTitle == "Login"
    assert surface.setEmptyHint("") is surface
    assert surface._emptyHint == ""


def test_a_click_gives_the_surface_focus(design):
    """So shortcuts scoped to the canvas, Delete above all, work."""
    assert design["surface"].focusPolicy() == Qt.FocusPolicy.ClickFocus


def test_palette_icons_follow_a_class_map(qapp, tmp_path):
    from PySide6.QtGui import QColor, QImage
    from limekit.widgets.widgetpalette import WidgetPalette

    icon = tmp_path / "button.png"
    image = QImage(16, 16, QImage.Format.Format_ARGB32)
    image.fill(QColor("#ff0000"))
    image.save(str(icon))

    palette = WidgetPalette()
    palette.setIcons({"ui.Button": str(icon)})
    items = {palette.list.item(i).text(): palette.list.item(i) for i in range(palette.list.count())}
    assert not items["Button"].icon().isNull()
    assert items["Label"].icon().isNull()


def test_palette_headers_read_as_enabled_text(qapp):
    """NoItemFlags painted the group headers in the disabled colour."""
    from limekit.widgets.widgetpalette import WidgetPalette
    palette = WidgetPalette()
    header = next(palette.list.item(i) for i in range(palette.list.count())
                  if palette.list.item(i).text() == "Inputs")
    assert header.flags() & Qt.ItemFlag.ItemIsEnabled
    assert not header.flags() & Qt.ItemFlag.ItemIsSelectable


def test_palette_groups_carry_their_ids_and_go_first_when_asked(qapp):
    from limekit.widgets.designsurface import CLASS_MIME
    from limekit.widgets.widgetpalette import WidgetPalette
    palette = WidgetPalette()
    palette.addGroup("Layouts", [{"id": "layout:ui.HLayout", "text": "Row", "tip": "side by side"}], True)
    assert palette.list.item(0).text() == "Layouts"
    row = palette.list.item(1)
    assert row.text() == "Row" and row.toolTip() == "side by side"
    mime = palette.list.mimeData([row])
    assert bytes(mime.data(CLASS_MIME)).decode() == "layout:ui.HLayout"
    picked = []
    palette.setOnPick(lambda cls: picked.append(cls))
    palette.list.itemDoubleClicked.emit(row)
    assert picked == ["layout:ui.HLayout"]
    palette.setFilter("row")
    assert not palette.list.item(0).isHidden() and not row.isHidden()


def test_labels_name_widgets_and_are_forgotten_with_the_design(design):
    surface = design["surface"]
    surface.setWidgetLabel(design["button"], "go · Button")
    assert surface._label(design["button"]) == "go · Button"
    assert surface._label(design["edit"]) == "LineEdit"
    surface.setDesignChild(design["box"])
    assert surface._label(design["button"]) == "Button"


def test_hover_follows_the_mouse_and_clears_on_leave(design):
    surface = design["surface"]
    point = centre_of(design["edit"], surface)
    move = QMouseEvent(QEvent.Type.MouseMove, QPointF(point), Qt.MouseButton.NoButton,
                       Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier)
    surface.mouseMoveEvent(move)
    assert surface._hover is design["edit"]
    surface.leaveEvent(QEvent(QEvent.Type.Leave))
    assert surface._hover is None


def test_a_moved_widget_drags_a_framed_labelled_picture(design):
    surface = design["surface"]
    surface.setWidgetLabel(design["button"], "go · Button")
    pixmap, hotspot = surface._drag_pixmap(design["button"], QPoint(5, 5))
    assert not pixmap.isNull()
    # Taller than the widget: the tag sits above it.
    assert pixmap.deviceIndependentSize().height() > design["button"].height()
    assert hotspot.y() > 5


def test_overlay_paints_every_state_without_error(design):
    """Hover, selection, a ghosted move, a target and a refusal, all at
    once -- the paint path must not trip over any combination."""
    from limekit.widgets.designsurface import resolve_drop
    surface = design["surface"]
    surface._hover = design["edit"]
    surface._selected = design["edit"]
    surface._dragging = design["button"]
    point = centre_of(design["edit"], surface)
    surface._cursor = point
    surface._pending = resolve_drop(surface, point, design["button"])
    assert surface._pending is not None
    surface._overlay.grab()
    surface._pending = None             # refused: a cursor with no slot
    surface._overlay.grab()


def test_widgets_in_a_design_never_take_keyboard_focus(design):
    """A focused LineEdit in the design claimed Delete and Ctrl+C as text
    editing, so the designer's shortcuts went into the design instead."""
    assert design["edit"].focusPolicy() == Qt.FocusPolicy.NoFocus
    assert design["box"].focusPolicy() == Qt.FocusPolicy.NoFocus


def test_a_replaced_design_is_deleted_not_left_as_a_window(design):
    """Detached, the old tree became a hidden top-level window that Qt could
    show again -- it took activation, and every shortcut, from the designer."""
    from shiboken6 import isValid
    from limekit.widgets.container import Container
    surface, old = design["surface"], design["box"]
    surface.setDesignChild(Container())
    QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete.value)
    QApplication.processEvents()
    assert not isValid(old)
    assert not any(w.isVisible() for w in QApplication.topLevelWidgets()
                   if type(w).__name__ == "Container")


def test_setting_the_same_design_again_keeps_it(design):
    from shiboken6 import isValid
    surface, box = design["surface"], design["box"]
    surface.setDesignChild(box)
    QApplication.processEvents()
    assert isValid(box) and surface.getDesignChild() is box


def test_tree_set_current_item_selects_and_clears(qapp):
    from limekit.widgets.treeview import TreeView, TreeViewItem
    tree = TreeView()
    a, b = TreeViewItem(["a"]), TreeViewItem(["b"])
    tree.addTopItem(a)
    tree.addTopItem(b)
    clicked = []
    tree.itemClicked.connect(lambda *args: clicked.append(args))
    tree.setCurrentItem(b)
    assert tree.getCurrentItem() is b
    tree.setCurrentItem(None)
    assert tree.selectedItems() == []
    assert clicked == []


def test_table_row_headers_can_be_hidden(qapp):
    from limekit.widgets.table import Table
    table = Table(2, 2)
    table.show()
    assert table.setRowHeadersVisible(False) is table
    assert not table.verticalHeader().isVisible()


def test_a_table_cell_can_be_locked_while_others_edit(qapp):
    from limekit.widgets.table import Table
    table = Table(1, 2)
    table.setCellsEditable(True)
    table.setCellText(1, 1, "label")
    table.setCellText(1, 2, "value")
    table.getCellItem(1, 1).setEditable(False)
    assert not table.getCellItem(1, 1).flags() & Qt.ItemFlag.ItemIsEditable
    assert table.getCellItem(1, 2).flags() & Qt.ItemFlag.ItemIsEditable


def test_textfield_takes_a_family_and_size_like_label(qapp):
    """The Build dialog's output box did field:setFont("Consolas", 9) and
    got Qt's one-argument setFont."""
    from limekit.widgets.textfield import TextField
    field = TextField()
    assert field.setFont("Consolas", 9) is field
    assert field.font().family() == "Consolas" and field.font().pointSize() == 9


def test_splitter_reports_user_moves_only(qapp):
    from limekit.widgets.splitter import Splitter
    from limekit.widgets.container import Container
    split = Splitter("vertical")
    split.addChild(Container())
    split.addChild(Container())
    moved = []
    split.setOnMove(lambda *args: moved.append(args))
    split.setSizes([100, 50])
    assert moved == []
    split.splitterMoved.emit(80, 1)
    assert len(moved) == 1


def test_handles_show_a_resize_cursor(design):
    surface = design["surface"]
    surface.setSelected(design["button"])
    handle = surface._handles()["right"].center()
    move = QMouseEvent(QEvent.Type.MouseMove, QPointF(handle), Qt.MouseButton.NoButton,
                       Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier)
    surface.mouseMoveEvent(move)
    assert surface.cursor().shape() == Qt.CursorShape.SizeHorCursor
    away = QMouseEvent(QEvent.Type.MouseMove, QPointF(3, 3), Qt.MouseButton.NoButton,
                       Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier)
    surface.mouseMoveEvent(away)
    assert surface.cursor().shape() == Qt.CursorShape.ArrowCursor
