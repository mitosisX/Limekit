"""Where a drop lands: the container under the cursor, and the slot in it."""

import pytest
from PySide6.QtCore import QMimeData, QPoint, QPointF, Qt
from PySide6.QtGui import QDropEvent
from PySide6.QtWidgets import QApplication

from limekit.kernel import manifest


@pytest.fixture(scope="module", autouse=True)
def qapp():
    manifest.import_all()
    return QApplication.instance() or QApplication([])


def show(surface):
    surface.resize(300, 300)
    surface.show()
    QApplication.processEvents()


def centre_of(widget, surface):
    return widget.mapTo(surface, widget.rect().center())


def class_drop_event(point, class_name):
    from limekit.widgets.designsurface import CLASS_MIME
    mime = QMimeData()
    mime.setData(CLASS_MIME, class_name.encode())
    event = QDropEvent(QPointF(point), Qt.DropAction.CopyAction, mime,
                       Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    # The event does not own its mime data; without this reference Python
    # collects it and mimeData() hands back a dead QObject.
    event._mime = mime
    return event


@pytest.fixture
def vbox(qapp):
    from limekit.layouts.vlayout import VLayout
    from limekit.widgets.button import Button
    from limekit.widgets.container import Container
    from limekit.widgets.designsurface import DesignSurface

    surface, box, layout = DesignSurface(), Container(), VLayout()
    buttons = [Button(f"b{i}") for i in range(3)]
    for b in buttons:
        layout.addChild(b)
    box.setLayout(layout)
    surface.setDesignChild(box)
    show(surface)
    return surface, box, buttons


@pytest.fixture
def nested(qapp):
    from limekit.layouts.vlayout import VLayout
    from limekit.widgets.button import Button
    from limekit.widgets.container import Container
    from limekit.widgets.designsurface import DesignSurface

    surface = DesignSurface()
    outer, outer_layout = Container(), VLayout()
    outer_layout.setMargins(20, 20, 20, 20)
    inner, inner_layout = Container(), VLayout()
    button = Button("in")
    inner_layout.addChild(button)
    inner.setLayout(inner_layout)
    outer_layout.addChild(inner)
    outer.setLayout(outer_layout)
    surface.setDesignChild(outer)
    show(surface)
    return surface, outer, inner, button


# -- resolution ---------------------------------------------------------------

def test_vbox_before_the_midpoint_of_the_second_child_is_slot_two(vbox):
    from limekit.widgets.designsurface import resolve_drop
    surface, box, buttons = vbox
    top = buttons[1].mapTo(surface, buttons[1].rect().topLeft())
    slot = resolve_drop(surface, QPoint(top.x() + 5, top.y() + 2))
    assert slot["target"] is box
    assert slot["layout"] == "vbox"
    assert slot["index"] == 2


def test_vbox_after_the_midpoint_of_the_last_child_is_the_end(vbox):
    from limekit.widgets.designsurface import resolve_drop
    surface, box, buttons = vbox
    bottom = buttons[2].mapTo(surface, buttons[2].rect().bottomLeft())
    slot = resolve_drop(surface, QPoint(bottom.x() + 5, bottom.y() - 2))
    assert slot["index"] == 4


def test_hbox_cuts_along_x(qapp):
    from limekit.layouts.hlayout import HLayout
    from limekit.widgets.button import Button
    from limekit.widgets.container import Container
    from limekit.widgets.designsurface import DesignSurface, resolve_drop

    surface, box, layout = DesignSurface(), Container(), HLayout()
    a, b = Button("a"), Button("b")
    layout.addChild(a)
    layout.addChild(b)
    box.setLayout(layout)
    surface.setDesignChild(box)
    show(surface)

    left = b.mapTo(surface, b.rect().topLeft())
    slot = resolve_drop(surface, QPoint(left.x() + 2, left.y() + 5))
    assert slot["layout"] == "hbox"
    assert slot["index"] == 2
    right = b.mapTo(surface, b.rect().topRight())
    assert resolve_drop(surface, QPoint(right.x() - 2, right.y() + 5))["index"] == 3


def test_a_widget_with_no_layout_is_not_a_target(qapp):
    from limekit.widgets.designsurface import DesignSurface, resolve_drop
    from limekit.widgets.label import Label

    surface = DesignSurface()
    surface.setDesignChild(Label("alone"))
    show(surface)
    assert resolve_drop(surface, QPoint(10, 10)) is None


def test_grid_reports_the_cell_under_the_cursor_and_one_past_the_edge(qapp):
    from limekit.layouts.grid import GridLayout
    from limekit.widgets.button import Button
    from limekit.widgets.container import Container
    from limekit.widgets.designsurface import DesignSurface, resolve_drop

    surface, box, grid = DesignSurface(), Container(), GridLayout()
    cells = {}
    for r in (1, 2):
        for c in (1, 2):
            cells[r, c] = Button(f"{r},{c}")
            grid.addChild(cells[r, c], r, c)
    box.setLayout(grid)
    surface.setDesignChild(box)
    show(surface)

    slot = resolve_drop(surface, centre_of(cells[2, 1], surface))
    assert (slot["layout"], slot["row"], slot["column"]) == ("grid", 2, 1)

    edge = cells[1, 2].mapTo(surface, cells[1, 2].rect().topRight())
    past = resolve_drop(surface, QPoint(edge.x() + 3, edge.y() + 5))
    assert (past["row"], past["column"]) == (1, 3)


def test_form_cuts_at_row_midpoints(qapp):
    from limekit.layouts.formlayout import FormLayout
    from limekit.widgets.container import Container
    from limekit.widgets.designsurface import DesignSurface, resolve_drop
    from limekit.widgets.lineedit import LineEdit

    surface, box, form = DesignSurface(), Container(), FormLayout()
    first, second = LineEdit(), LineEdit()
    form.addChild("A", first)
    form.addChild("B", second)
    box.setLayout(form)
    surface.setDesignChild(box)
    show(surface)

    top = second.mapTo(surface, second.rect().topLeft())
    slot = resolve_drop(surface, QPoint(top.x() + 5, top.y() + 1))
    assert slot["layout"] == "form"
    assert slot["index"] == 2
    bottom = second.mapTo(surface, second.rect().bottomLeft())
    assert resolve_drop(surface, QPoint(bottom.x() + 5, bottom.y() - 1))["index"] == 3


def test_the_innermost_container_under_the_cursor_is_the_target(nested):
    from limekit.widgets.designsurface import resolve_drop
    surface, outer, inner, button = nested
    assert resolve_drop(surface, centre_of(button, surface))["target"] is inner
    assert resolve_drop(surface, QPoint(3, 3))["target"] is outer


def test_a_moved_widget_cannot_land_inside_itself(nested):
    from limekit.widgets.designsurface import resolve_drop
    surface, outer, inner, button = nested
    assert resolve_drop(surface, centre_of(button, surface), dragging=inner) is None
    assert resolve_drop(surface, QPoint(3, 3), dragging=inner)["target"] is outer


# -- events -------------------------------------------------------------------

def test_dropping_a_class_reports_it_and_adds_nothing(vbox):
    surface, box, buttons = vbox
    seen = []
    surface.setOnDrop(lambda drop: seen.append(drop))
    before = box.layout().count()

    surface.dropEvent(class_drop_event(centre_of(buttons[0], surface), "ui.Label"))

    assert box.layout().count() == before
    assert len(seen) == 1
    drop = seen[0]
    assert drop["kind"] == "class"
    assert drop["class"] == "ui.Label"
    assert drop["target"] is box
    assert drop["layout"] == "vbox"
    assert drop["index"] in (1, 2)


def test_a_drop_with_no_target_reaches_no_handler(qapp):
    from limekit.widgets.designsurface import DesignSurface
    from limekit.widgets.label import Label
    surface = DesignSurface()
    surface.setDesignChild(Label("alone"))
    show(surface)
    seen = []
    surface.setOnDrop(lambda drop: seen.append(drop))
    surface.dropEvent(class_drop_event(QPoint(5, 5), "ui.Button"))
    assert seen == []


def test_drop_can_be_switched_off(vbox):
    surface, box, buttons = vbox
    seen = []
    surface.setOnDrop(lambda drop: seen.append(drop))
    surface.setDropEnabled(False)
    surface.dropEvent(class_drop_event(centre_of(buttons[0], surface), "ui.Label"))
    assert seen == []


def test_the_indicator_is_a_bar_at_the_slot_boundary(vbox):
    from limekit.widgets.designsurface import indicator_rect
    surface, box, buttons = vbox
    slot = {"target": box, "layout": "vbox", "index": 2}
    rect = indicator_rect(surface, slot)
    boundary = buttons[1].mapTo(surface, buttons[1].rect().topLeft()).y()
    assert abs(rect.center().y() - boundary) <= 4
    assert rect.width() >= buttons[1].width()


def test_a_right_click_selects_and_offers_a_menu(vbox):
    from PySide6.QtCore import QEvent
    from PySide6.QtGui import QMouseEvent
    surface, box, buttons = vbox
    asked = []
    surface.setOnContextMenu(lambda widget, x, y: asked.append((widget, x, y)))
    point = centre_of(buttons[1], surface)
    event = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(point),
                        Qt.MouseButton.RightButton, Qt.MouseButton.RightButton,
                        Qt.KeyboardModifier.NoModifier)
    surface.mousePressEvent(event)
    assert surface.getSelected() is buttons[1]
    assert asked == [(buttons[1], point.x(), point.y())]
