"""A hit on a part of a widget is a hit on the widget.

Under the mouse, Qt's innermost widget is often a part the design never made
-- a Table's viewport, a Splitter's handle, a Tab's bar -- and the surface
used to report that part: the hover tag read "QWidget", and a click on a
Table's cells selected nothing the designer knew.
"""

import pytest
from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from limekit.kernel import manifest


@pytest.fixture(scope="module", autouse=True)
def qapp():
    manifest.import_all()
    return QApplication.instance() or QApplication([])


def _event(kind, point, button=Qt.MouseButton.LeftButton, buttons=None):
    buttons = button if buttons is None else buttons
    return QMouseEvent(kind, QPointF(point), button, buttons, Qt.KeyboardModifier.NoModifier)


def press(surface, point, button=Qt.MouseButton.LeftButton):
    surface.mousePressEvent(_event(QEvent.Type.MouseButtonPress, point, button))


def double_click(surface, point):
    surface.mouseDoubleClickEvent(_event(QEvent.Type.MouseButtonDblClick, point))


def hover(surface, point):
    surface.mouseMoveEvent(_event(QEvent.Type.MouseMove, point, Qt.MouseButton.NoButton,
                                  Qt.MouseButton.NoButton))


def inside(surface, widget, part=None):
    """A point on `part` of `widget` (its viewport, say), in surface coords."""
    target = part or widget
    return target.mapTo(surface, target.rect().center())


@pytest.fixture
def composites(qapp):
    """A column holding a Table, a Splitter with two panes, and a Tab."""
    from limekit.layouts.vlayout import VLayout
    from limekit.widgets.container import Container
    from limekit.widgets.designsurface import DesignSurface
    from limekit.widgets.label import Label
    from limekit.widgets.splitter import Splitter
    from limekit.widgets.tab import Tab
    from limekit.widgets.table import Table

    surface = DesignSurface()
    surface.resize(500, 700)
    box, layout = Container(), VLayout()
    table = Table(3, 2)
    splitter = Splitter("horizontal")
    left, right = Label("left"), Label("right")
    splitter.addChild(left)
    splitter.addChild(right)
    tab = Tab()
    page = Container()
    tab.addTab(page, "Page 1")
    for widget in (table, splitter, tab):
        layout.addChild(widget)
    box.setLayout(layout)
    box.setFixedSize(420, 600)
    surface.setDesignChild(box)
    surface.show()
    QApplication.processEvents()
    return {"surface": surface, "box": box, "table": table, "splitter": splitter,
            "left": left, "tab": tab, "page": page}


def label_all(d):
    """What Limer does: every design widget gets a name on the surface."""
    s = d["surface"]
    for key in ("box", "table", "splitter", "left", "tab", "page"):
        s.setWidgetLabel(d[key], key + "1 · " + type(d[key]).__name__)


@pytest.mark.parametrize("labelled", [True, False], ids=["labelled", "unlabelled"])
def test_a_click_on_a_tables_cells_selects_the_table(composites, labelled):
    d = composites
    if labelled:
        label_all(d)
    picked = []
    d["surface"].setOnSelect(lambda widget: picked.append(widget))
    press(d["surface"], inside(d["surface"], d["table"], d["table"].viewport()))
    assert d["surface"].getSelected() is d["table"]
    assert picked == [d["table"]]


def test_a_splitter_handle_and_a_tab_bar_are_their_widgets(composites):
    d = composites
    label_all(d)
    handle = d["splitter"].handle(1)
    press(d["surface"], inside(d["surface"], d["splitter"], handle))
    assert d["surface"].getSelected() is d["splitter"]
    press(d["surface"], inside(d["surface"], d["tab"], d["tab"].tabBar()))
    assert d["surface"].getSelected() is d["tab"]
    # A page is labelled, so a click on it is the page -- not the Tab, and
    # not the stack the Tab keeps its pages in.
    press(d["surface"], inside(d["surface"], d["page"]))
    assert d["surface"].getSelected() is d["page"]


def test_a_labelled_widget_inside_a_composite_still_wins(composites):
    """Climbing stops at the first design widget, not at the top one."""
    d = composites
    label_all(d)
    press(d["surface"], inside(d["surface"], d["left"]))
    assert d["surface"].getSelected() is d["left"]


def test_double_click_and_context_menu_climb_too(composites):
    d = composites
    label_all(d)
    doubled, menus = [], []
    d["surface"].setOnDoubleClick(lambda widget, x, y: doubled.append(widget))
    d["surface"].setOnContextMenu(lambda widget, x, y: menus.append(widget))
    point = inside(d["surface"], d["table"], d["table"].viewport())
    double_click(d["surface"], point)
    press(d["surface"], point, Qt.MouseButton.RightButton)
    assert doubled == [d["table"]]
    assert menus == [d["table"]]


def test_hover_names_the_widget_never_a_qt_class(composites):
    d = composites
    s = d["surface"]
    hover(s, inside(s, d["table"], d["table"].viewport()))
    assert s._hover is d["table"]
    # Unlabelled, the tag is Limekit's name for the class, never Qt's.
    assert s._label(s._hover) == "Table"
    label_all(d)
    assert s._label(d["table"]) == "table1 · Table"
    assert not s._label(d["splitter"].handle(1)).startswith("Q")


def test_empty_surface_is_still_nothing(composites):
    s = composites["surface"]
    press(s, QPoint(2, 2))
    assert s.getSelected() is None


def test_a_drop_on_a_composite_lands_beside_it_not_inside_it(qapp):
    """A Calendar is a QVBoxLayout of parts on the inside. Only Limekit's own
    layouts and holders are containers in a design, so a drop on it is a
    slot in the column around it -- and it gets no container outline."""
    from limekit.layouts.vlayout import VLayout
    from limekit.widgets.calendar import Calendar
    from limekit.widgets.container import Container
    from limekit.widgets.designsurface import DesignSurface, container_frames, resolve_drop

    surface = DesignSurface()
    surface.resize(500, 500)
    box, layout = Container(), VLayout()
    calendar = Calendar()
    layout.addChild(calendar)
    box.setLayout(layout)
    surface.setDesignChild(box)
    surface.show()
    QApplication.processEvents()

    slot = resolve_drop(surface, inside(surface, calendar))
    assert slot["target"] is box and slot["layout"] == "vbox"
    assert [widget for widget, _ in container_frames(surface)] == [box]
