"""Tabs, splitters and scrollers as drop targets; handles and double-click."""

import pytest
from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QMouseEvent
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


def mouse(kind, point, button=Qt.MouseButton.LeftButton, buttons=None):
    if buttons is None:
        buttons = button
    return QMouseEvent(kind, QPointF(point), button, buttons, Qt.KeyboardModifier.NoModifier)


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


# -- holders ------------------------------------------------------------------

def test_a_tab_with_no_pages_takes_a_new_page(qapp):
    from limekit.widgets.designsurface import DesignSurface, resolve_drop
    from limekit.widgets.tab import Tab
    surface, tab = DesignSurface(), Tab()
    surface.setDesignChild(tab)
    show(surface)
    slot = resolve_drop(surface, QPoint(150, 150))
    assert slot["target"] is tab
    assert slot["layout"] == "tab"
    assert slot["index"] == 1


def test_a_page_with_a_layout_is_the_target_inside_a_tab(qapp):
    from limekit.layouts.vlayout import VLayout
    from limekit.widgets.button import Button
    from limekit.widgets.container import Container
    from limekit.widgets.designsurface import DesignSurface, resolve_drop
    from limekit.widgets.tab import Tab
    surface, tab, page = DesignSurface(), Tab(), Container()
    layout = VLayout()
    button = Button("in page")
    layout.addChild(button)
    page.setLayout(layout)
    tab.addTab(page, "One")
    surface.setDesignChild(tab)
    show(surface)
    slot = resolve_drop(surface, centre_of(button, surface))
    assert slot["target"] is page and slot["layout"] == "vbox"
    bar = tab.tabBar()
    on_bar = bar.mapTo(surface, bar.tabRect(0).center())
    assert resolve_drop(surface, on_bar)["target"] is tab


def test_splitter_panes_cut_at_midpoints(qapp):
    from limekit.widgets.designsurface import DesignSurface, resolve_drop
    from limekit.widgets.label import Label
    from limekit.widgets.splitter import Splitter
    surface, split = DesignSurface(), Splitter("horizontal")
    a, b = Label("a"), Label("b")
    split.addChild(a)
    split.addChild(b)
    surface.setDesignChild(split)
    show(surface)
    left = b.mapTo(surface, b.rect().topLeft())
    slot = resolve_drop(surface, QPoint(left.x() + 2, left.y() + 5))
    assert slot["target"] is split and slot["layout"] == "splitter" and slot["index"] == 2
    right = b.mapTo(surface, b.rect().topRight())
    assert resolve_drop(surface, QPoint(right.x() - 2, right.y() + 5))["index"] == 3


def test_a_scroller_is_a_target_with_one_slot(qapp):
    from limekit.widgets.designsurface import DesignSurface, resolve_drop
    from limekit.widgets.scroller import Scroller
    surface, scroller = DesignSurface(), Scroller()
    surface.setDesignChild(scroller)
    show(surface)
    slot = resolve_drop(surface, QPoint(100, 100))
    assert slot["target"] is scroller and slot["layout"] == "scroller" and slot["index"] == 1


def test_holders_are_outlined(qapp):
    from limekit.widgets.designsurface import DesignSurface, container_frames
    from limekit.widgets.tab import Tab
    surface, tab = DesignSurface(), Tab()
    surface.setDesignChild(tab)
    show(surface)
    assert tab in [w for w, _ in container_frames(surface)]


# -- handles and double-click -------------------------------------------------

def test_dragging_the_corner_handle_reports_a_size(vbox):
    surface, box, buttons = vbox
    sizes = []
    surface.setOnResize(lambda widget, w, h: sizes.append((widget, w, h)))
    surface.mousePressEvent(mouse(QEvent.Type.MouseButtonPress, centre_of(buttons[0], surface)))
    corner = surface._handles()["corner"].center()
    surface.mousePressEvent(mouse(QEvent.Type.MouseButtonPress, corner))
    assert surface._resizing is not None
    moved = QPoint(corner.x() + 40, corner.y() + 20)
    surface.mouseMoveEvent(mouse(QEvent.Type.MouseMove, moved))
    surface.mouseReleaseEvent(mouse(QEvent.Type.MouseButtonRelease, moved,
                                    buttons=Qt.MouseButton.NoButton))
    assert sizes and sizes[0][0] is buttons[0]
    assert sizes[0][1] == buttons[0].width() + 40
    assert sizes[0][2] == buttons[0].height() + 20
    assert surface.getSelected() is buttons[0]       # the handle press did not reselect


def test_the_design_child_has_no_handles(vbox):
    surface, box, buttons = vbox
    surface.setSelected(box)
    assert surface._handles() == {}


def test_double_click_reports_the_widget(vbox):
    surface, box, buttons = vbox
    seen = []
    surface.setOnDoubleClick(lambda widget, x, y: seen.append(widget))
    point = centre_of(buttons[2], surface)
    surface.mouseDoubleClickEvent(mouse(QEvent.Type.MouseButtonDblClick, point))
    assert seen == [buttons[2]]
