"""Zoom, snapping, guides and multiple selection on the design surface."""

import pytest
from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QMouseEvent, QWheelEvent
from PySide6.QtWidgets import QApplication

from limekit.kernel import manifest
from limekit.kernel.bridge.convert import as_sequence, to_py

NO = Qt.KeyboardModifier.NoModifier
CTRL = Qt.KeyboardModifier.ControlModifier
LEFT = Qt.MouseButton.LeftButton


@pytest.fixture(scope="module", autouse=True)
def qapp():
    manifest.import_all()
    return QApplication.instance() or QApplication([])


def _mouse(surface, kind, point, mods=NO, buttons=LEFT, button=LEFT):
    event = QMouseEvent(kind, QPointF(point), button, buttons, mods)
    {QEvent.Type.MouseButtonPress: surface.mousePressEvent,
     QEvent.Type.MouseMove: surface.mouseMoveEvent,
     QEvent.Type.MouseButtonRelease: surface.mouseReleaseEvent}[kind](event)


def press(s, p, mods=NO):
    _mouse(s, QEvent.Type.MouseButtonPress, p, mods)


def move(s, p, mods=NO):
    _mouse(s, QEvent.Type.MouseMove, p, mods)


def release(s, p, mods=NO):
    _mouse(s, QEvent.Type.MouseButtonRelease, p, mods, buttons=Qt.MouseButton.NoButton)


def click(s, p, mods=NO):
    press(s, p, mods)
    release(s, p, mods)


def drag(s, start, end, mods=NO):
    press(s, start, mods)
    move(s, QPoint((start.x() + end.x()) // 2, (start.y() + end.y()) // 2), mods)
    move(s, end, mods)
    release(s, end, mods)


@pytest.fixture
def design(qapp):
    """A 400x300 column: two buttons, then a row holding a label and a line edit."""
    from limekit.layouts.hlayout import HLayout
    from limekit.layouts.vlayout import VLayout
    from limekit.widgets.button import Button
    from limekit.widgets.container import Container
    from limekit.widgets.designsurface import DesignSurface
    from limekit.widgets.label import Label
    from limekit.widgets.lineedit import LineEdit

    surface = DesignSurface()
    surface.resize(1200, 1000)
    box, layout = Container(), VLayout()
    first, second = Button("first"), Button("second")
    row, row_layout = Container(), HLayout()
    label, edit = Label("name"), LineEdit("")
    row_layout.addChild(label)
    row_layout.addChild(edit)
    row.setLayout(row_layout)
    for widget in (first, second, row):
        layout.addChild(widget)
    box.setLayout(layout)
    box.setFixedSize(400, 300)
    surface.setDesignChild(box)
    for widget, name in ((box, "root"), (first, "first"), (second, "second"),
                         (row, "row"), (label, "label"), (edit, "edit")):
        surface.setWidgetLabel(widget, name)
    surface.show()
    QApplication.processEvents()
    return {"surface": surface, "box": box, "first": first, "second": second,
            "row": row, "label": label, "edit": edit}


def py(value):
    """A list from what the surface hands back: a Lua table once a runtime is
    bound -- as it is for every Lua caller -- or a plain list before."""
    return [to_py(item) if not hasattr(item, "isWidgetType") else item for item in as_sequence(value)]


def centre(surface, widget):
    return surface._rect_in(widget).center()


# -- zoom ---------------------------------------------------------------------

def test_zoom_scales_where_the_design_is_drawn_not_the_widgets(design):
    s, box = design["surface"], design["box"]
    real = s._rect_in(design["first"])
    s.setZoom(2)
    assert s.getZoom() == 2.0
    assert s._design_rect().size().toTuple() == (800, 600)
    assert box.size().toTuple() == (400, 300), "the widgets keep their real size"
    zoomed = s._rect_in(design["first"])
    assert (zoomed.width(), zoomed.height()) == (real.width() * 2, real.height() * 2)
    s.resetZoom()
    assert s.getZoom() == 1.0 and box.parentWidget() is s
    assert s._rect_in(design["first"]) == real


def test_zoom_is_clamped_and_steps(design):
    s = design["surface"]
    s.setZoom(10)
    assert s.getZoom() == 3.0
    s.setZoom(0.01)
    assert s.getZoom() == 0.25
    s.setZoom(1)
    s.zoomIn()
    assert s.getZoom() == 1.1
    s.zoomOut()
    s.zoomOut()
    assert s.getZoom() == 0.9


@pytest.mark.parametrize("zoom", [0.5, 2.0])
def test_a_click_selects_what_is_drawn_there_at_any_zoom(design, zoom):
    s = design["surface"]
    s.setZoom(zoom)
    for name in ("first", "second", "label", "edit"):
        click(s, centre(s, design[name]))
        assert s.getSelected() is design[name], f"{name} at {zoom}"


@pytest.mark.parametrize("zoom", [0.5, 2.0])
def test_a_drop_lands_in_the_slot_drawn_under_it(design, zoom):
    from limekit.widgets.designsurface import resolve_drop
    s = design["surface"]
    s.setZoom(zoom)
    between = s._rect_in(design["second"]).topLeft() + QPoint(5, 1)
    slot = resolve_drop(s, between)
    assert slot["target"] is design["box"] and slot["index"] == 2


def test_a_resize_at_double_zoom_reports_real_pixels(design):
    s = design["surface"]
    s.setZoom(2)
    s.setGuidesEnabled(False)
    reported = []
    s.setOnResize(lambda widget, w, h: reported.append((widget, w, h)))
    click(s, centre(s, design["first"]))
    width = design["first"].width()
    handle = s._handles()["right"].center()
    drag(s, handle, handle + QPoint(40, 0))
    assert reported and reported[0][0] is design["first"]
    assert reported[0][1] == width + 20, "40 screen px at 2x is 20 real px"


def test_ctrl_wheel_zooms_and_says_so(design):
    s = design["surface"]
    heard = []
    s.setOnZoomChange(lambda factor: heard.append(factor))
    at = QPointF(50, 50)
    up = QWheelEvent(at, s.mapToGlobal(at), QPoint(), QPoint(0, 120), Qt.MouseButton.NoButton,
                     CTRL, Qt.ScrollPhase.NoScrollPhase, False)
    s.wheelEvent(up)
    assert s.getZoom() == 1.1 and heard == [1.1]


def test_a_zoomed_design_is_painted(design):
    s = design["surface"]
    s.setZoom(0.5)
    QApplication.processEvents()
    image = s.grab().toImage()
    drawn = s._rect_in(design["first"])
    colours = {image.pixelColor(x, y).rgb()
               for x in range(drawn.left(), drawn.right(), 2) for y in range(drawn.top(), drawn.bottom(), 2)}
    # A flat fill would be one colour; a button -- its border, its text -- is several.
    assert len(colours) > 2, "the button is drawn, scaled, where it belongs"


# -- grid and guides ------------------------------------------------------------

def test_a_resize_snaps_to_the_grid(design):
    s = design["surface"]
    s.setGuidesEnabled(False)
    s.setSnapToGrid(True)
    s.setGridSize(10)
    reported = []
    s.setOnResize(lambda widget, w, h: reported.append(h))
    click(s, centre(s, design["first"]))
    handle = s._handles()["bottom"].center()
    drag(s, handle, handle + QPoint(0, 23))
    assert reported and reported[0] % 10 == 0


def test_a_pulled_edge_snaps_to_a_neighbours_edge_and_shows_a_guide(design):
    """In a column every widget's right edge lines up; pulled 3 px past it,
    the edge is caught by the guide and stays where the others end."""
    s = design["surface"]
    click(s, centre(s, design["first"]))
    handle = s._handles()["right"].center()
    press(s, handle)
    move(s, handle + QPoint(3, 0))
    assert s._guides, "a guide is shown"
    assert s._resizeSize[0] == design["first"].width()
    release(s, handle + QPoint(3, 0))
    assert not s._guides


def test_without_guides_the_same_pull_is_taken_as_given(design):
    s = design["surface"]
    s.setGuidesEnabled(False)
    reported = []
    s.setOnResize(lambda widget, w, h: reported.append(w))
    click(s, centre(s, design["first"]))
    width = design["first"].width()
    handle = s._handles()["right"].center()
    drag(s, handle, handle + QPoint(3, 0))
    assert reported == [width + 3]


# -- several at once ------------------------------------------------------------

def test_ctrl_click_adds_and_takes_away(design):
    s = design["surface"]
    heard = []
    s.setOnSelectionChange(lambda widgets: heard.append(py(widgets)))
    click(s, centre(s, design["first"]))
    click(s, centre(s, design["label"]), CTRL)
    assert py(s.getSelection()) == [design["first"], design["label"]]
    assert s.getSelected() is design["label"], "the last one is the primary"
    assert heard[-1] == [design["first"], design["label"]]
    click(s, centre(s, design["first"]), CTRL)
    assert py(s.getSelection()) == [design["label"]]


def test_a_marquee_takes_the_outermost_widgets_it_encloses(design):
    s = design["surface"]
    heard = []
    s.setOnSelectionChange(lambda widgets: heard.append(py(widgets)))
    top_left = s._rect_in(design["second"]).topLeft() - QPoint(2, 2)
    bottom_right = s._rect_in(design["row"]).bottomRight() + QPoint(2, 2)
    start = QPoint(s._design_rect().left() - 10, top_left.y())   # off the design, on the backdrop
    drag(s, start, bottom_right)
    # The row is taken whole; its label and line edit come with it, not besides it.
    assert py(s.getSelection()) == [design["second"], design["row"]]
    assert heard[-1] == [design["second"], design["row"]]


def test_a_marquee_that_takes_nothing_leaves_the_selection_alone(design):
    s = design["surface"]
    click(s, centre(s, design["first"]))
    corner = QPoint(5, 5)
    drag(s, corner, corner + QPoint(20, 20))
    assert s.getSelected() is None   # a press on the empty surface selects nothing


def test_a_press_on_one_of_several_keeps_them_until_released(design):
    s = design["surface"]
    s.setSelection([design["first"], design["second"]])
    press(s, centre(s, design["first"]))
    assert py(s.getSelection()) == [design["first"], design["second"]], "still both: maybe a move"
    release(s, centre(s, design["first"]))
    assert py(s.getSelection()) == [design["first"]]


def test_a_resize_pulls_every_selected_widget_by_the_same_amount(design):
    s = design["surface"]
    s.setGuidesEnabled(False)
    reported = []
    s.setOnResizeSelection(lambda sizes: reported.extend(py(sizes)))
    s.setSelection([design["label"], design["first"]])
    first_w, label_w = design["first"].width(), design["label"].width()
    handle = s._handles()["right"].center()
    drag(s, handle, handle - QPoint(30, 0))
    by = {entry["widget"]: entry["width"] for entry in reported}
    assert by == {design["first"]: first_w - 30, design["label"]: label_w - 30}


def test_a_drop_never_lands_inside_anything_being_moved(design):
    from limekit.widgets.designsurface import resolve_drop
    s = design["surface"]
    inside_row = centre(s, design["edit"])
    assert resolve_drop(s, inside_row, [design["first"], design["row"]]) is None
    assert resolve_drop(s, inside_row, [design["first"]]) is not None


def test_get_widget_size_is_real_pixels_at_any_zoom(design):
    s = design["surface"]
    real = s.getWidgetSize(design["first"])
    s.setZoom(2)
    assert s.getWidgetSize(design["first"]) == real == (design["first"].width(), design["first"].height())


def test_a_layout_aligns_one_child_and_lets_it_fill_again(design):
    from limekit.kernel.errors import BridgeError
    from limekit.widgets.button import Button
    box, first = design["box"], design["first"]
    layout = box.layout()
    filling = first.width()
    layout.setChildAlignment(first, "right")
    layout.activate()
    assert first.width() < filling and first.geometry().right() == layout.contentsRect().right()
    layout.setChildAlignment(first)
    layout.activate()
    assert first.width() == filling
    with pytest.raises(BridgeError):
        layout.setChildAlignment(Button("stray"), "left")
