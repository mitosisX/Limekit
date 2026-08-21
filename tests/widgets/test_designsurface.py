"""Clicking a designed widget must select it, not use it."""

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
    from limekit.widgets.label import Label

    surface = DesignSurface()
    surface.resize(300, 200)

    box, layout = Container(), VLayout()
    label, button = Label("hello"), Button("press")
    layout.addChild(label)
    layout.addChild(button)
    box.setLayout(layout)

    surface.setDesignChild(box)
    surface.show()
    QApplication.processEvents()

    return {"surface": surface, "box": box, "label": label, "button": button}


def click(surface, point):
    event = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(point),
                        Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
                        Qt.KeyboardModifier.NoModifier)
    surface.mousePressEvent(event)


def test_every_designed_widget_is_out_of_the_mouses_reach(design):
    """A single interactive widget in a design is worse than none."""
    attribute = Qt.WidgetAttribute.WA_TransparentForMouseEvents
    assert design["box"].testAttribute(attribute)
    assert design["label"].testAttribute(attribute)
    assert design["button"].testAttribute(attribute)


def test_a_button_in_a_design_does_not_fire_when_clicked(design):
    """The point of the whole surface."""
    fired = []
    design["button"].setOnClick(lambda *_: fired.append(True))

    centre = design["button"].mapTo(design["surface"], design["button"].rect().center())
    click(design["surface"], centre)

    assert fired == []
    assert design["surface"].getSelected() is design["button"]


def test_clicking_the_label_selects_the_label(design):
    centre = design["label"].mapTo(design["surface"], design["label"].rect().center())
    click(design["surface"], centre)
    assert design["surface"].getSelected() is design["label"]


def test_the_deepest_widget_wins_not_the_container_holding_it(design):
    """The trap childAt falls into, kept as a test so it stays fixed."""
    for name in ("label", "button"):
        target = design[name]
        centre = target.mapTo(design["surface"], target.rect().center())
        click(design["surface"], centre)
        assert design["surface"].getSelected() is target, name


def test_the_handler_is_told_what_was_picked(design):
    picked = []
    design["surface"].setOnSelect(lambda widget: picked.append(widget))

    centre = design["button"].mapTo(design["surface"], design["button"].rect().center())
    click(design["surface"], centre)

    assert picked == [design["button"]]


def test_a_widget_built_after_the_design_was_set_is_made_inert_by_refresh(design):
    from limekit.widgets.button import Button

    late = Button("late")
    design["box"].getLayout().addChild(late)
    QApplication.processEvents()

    assert not late.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    design["surface"].refresh()
    assert late.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)


def test_replacing_the_design_child_clears_the_selection(design):
    from limekit.widgets.label import Label

    centre = design["button"].mapTo(design["surface"], design["button"].rect().center())
    click(design["surface"], centre)
    assert design["surface"].getSelected() is not None

    design["surface"].setDesignChild(Label("fresh"))
    assert design["surface"].getSelected() is None
