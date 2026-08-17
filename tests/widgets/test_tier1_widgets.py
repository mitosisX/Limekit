"""Tier-1 widgets: construction, prop round-trips, guarded events, 1-indexing.

Mirrors the conventions in test_pilot_widgets.py. The `qapp` fixture comes
from tests/conftest.py; the `sink` fixture (captures guarded errors instead
of printing them) comes from tests/widgets/test_pilot_widgets.py's module,
so it's redeclared here identically rather than imported across test files.
"""

import pytest

from limekit.kernel.bridge.guard import reset_error_sink, set_error_sink
from limekit.kernel.errors import BridgeError, RegistryError


@pytest.fixture(autouse=True)
def sink():
    captured = []
    set_error_sink(captured.append)
    yield captured
    reset_error_sink()


# -- LineEdit ----------------------------------------------------------------

def test_lineedit_text_and_props_round_trip(qapp):
    from limekit.widgets.lineedit import LineEdit
    field = LineEdit("hi")
    assert field.getText() == "hi"
    field.setText(42)                       # coerced like Button.setText
    assert field.getText() == "42"
    field.setReadOnly(True)
    assert field.isReadOnly() is True
    field.setMaxLength(5)
    assert field.getMaxLength() == 5
    field.setHint("type here")
    assert field.getHint() == "type here"
    field.setInputMode("password")
    from PySide6.QtWidgets import QLineEdit
    assert field.getInputMode() == QLineEdit.EchoMode.Password


def test_lineedit_setters_chain(qapp):
    from limekit.widgets.lineedit import LineEdit
    field = LineEdit()
    assert field.setText("x").selectAll().clear() is field


def test_lineedit_onreturnpress_is_guarded(qapp, sink):
    from limekit.widgets.lineedit import LineEdit
    field = LineEdit()
    field.setOnReturnPress(lambda *a: 1 / 0)
    field.returnPressed.emit()
    assert len(sink) == 1


# -- GroupBox ------------------------------------------------------------

def test_groupbox_props_round_trip(qapp):
    from limekit.widgets.groupbox import GroupBox
    from limekit.widgets.button import Button
    box = GroupBox("Settings")
    assert box.getTitle() == "Settings"
    box.setCheckable(True)
    assert box.isCheckable() is True
    box.setChecked(True)
    assert box.isChecked() is True
    box.setFlat(True)
    assert box.isFlat() is True

    from limekit.layouts.vlayout import VLayout
    layout = VLayout()
    layout.addChild(Button("a"))
    box.setLayout(layout)
    assert box.getLayout() is layout


# -- FormLayout (1-indexed) -----------------------------------------------

def test_formlayout_addchild_and_rows_are_1_indexed(qapp):
    from limekit.layouts.formlayout import FormLayout
    from limekit.widgets.lineedit import LineEdit

    form = FormLayout()
    first = LineEdit("first")
    second = LineEdit("second")
    form.addChild("First", first)
    form.addChild("Second", second)

    assert form.getCount() == 4                  # 2 labels + 2 fields
    assert form.getRowAt(1) is first
    assert form.getRowAt(2) is second

    with pytest.raises(BridgeError):
        form.getRowAt(0)                          # 1-indexed, 0 is out of range


def test_formlayout_addchild_accepts_bare_widget(qapp):
    from limekit.layouts.formlayout import FormLayout
    from limekit.widgets.label import Label

    form = FormLayout()
    label = Label("standalone")
    form.addChild(label)
    assert form.getRowAt(1) is label


# -- Container -------------------------------------------------------------

def test_container_layout_prop_and_onkeypress(qapp, sink):
    from limekit.widgets.container import Container
    from limekit.layouts.vlayout import VLayout

    box = Container()
    layout = VLayout()
    assert box.setLayout(layout) is box
    assert box.getLayout() is layout

    box.setOnKeyPress(lambda *a: 1 / 0)
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent
    event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_A, Qt.KeyboardModifier.NoModifier)
    box.keyPressEvent(event)
    assert len(sink) == 1


def test_container_onkeypress_does_not_swallow_default_handling(qapp, sink):
    """Attaching a key handler must not switch off Qt's own key processing.

    The handler used to run *instead of* super().keyPressEvent(), so a
    Container with an onKeyPress handler consumed every key press: nothing
    inside it -- a LineEdit especially -- saw input again.

    QWidget.keyPressEvent ignores the event so it can propagate onwards, so
    "super() ran" is observable as the event no longer being accepted. With
    super() skipped, the event stays accepted and propagation stops dead.
    """
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent

    from limekit.widgets.container import Container

    def press(box):
        event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_A,
                          Qt.KeyboardModifier.NoModifier)
        assert event.isAccepted()        # a fresh QKeyEvent starts accepted
        box.keyPressEvent(event)
        return event

    seen = []
    handled = Container()
    handled.setOnKeyPress(lambda *a: seen.append("handler"))

    event = press(handled)

    assert seen == ["handler"]           # the handler still runs
    assert not sink                      # and did not raise
    assert not event.isAccepted()        # and Qt still got its turn

    # Identical to a Container with no handler attached at all.
    assert press(Container()).isAccepted() is False


# -- Image -------------------------------------------------------------------

def test_image_alignment_and_click_guarded(qapp, sink):
    from limekit.widgets.image import Image
    img = Image()
    assert img.getImagePath() == ""
    img.setImageAlignment("center", "top")
    img.setOnClick(lambda *a: 1 / 0)
    from PySide6.QtCore import QEvent, QPoint, Qt
    from PySide6.QtGui import QMouseEvent
    event = QMouseEvent(QEvent.Type.MouseButtonPress, QPoint(0, 0), Qt.MouseButton.LeftButton,
                         Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    img.mousePressEvent(event)
    assert len(sink) == 1


def test_image_setimagesize_without_image_raises_bridge_error(qapp):
    from limekit.widgets.image import Image
    img = Image()
    with pytest.raises(BridgeError):
        img.setImageSize(10, 10)


# -- Spinner / DoubleSpinner -------------------------------------------------

def test_spinner_value_and_range(qapp):
    from limekit.widgets.spinner import Spinner
    spin = Spinner()
    spin.setRange(0, 10)
    spin.setValue(5)
    assert spin.getValue() == 5
    spin.setPrefix("$")
    assert spin.getPrefix() == "$"


def test_spinner_onvaluechange_guarded(qapp, sink):
    from limekit.widgets.spinner import Spinner
    spin = Spinner()
    spin.setOnValueChange(lambda *a: 1 / 0)
    spin.setValue(7)
    assert len(sink) == 1


def test_doublespinner_value_is_float(qapp):
    from limekit.widgets.doublespinner import DoubleSpinner
    spin = DoubleSpinner()
    spin.setRange(0.0, 1.0)
    spin.setValue(0.5)
    assert spin.getValue() == pytest.approx(0.5)


def test_doublespinner_range_rejects_non_numeric(qapp):
    from limekit.widgets.doublespinner import DoubleSpinner
    with pytest.raises(BridgeError):
        DoubleSpinner().setRange("a", 1.0)


# -- ProgressBar ---------------------------------------------------------

def test_progressbar_value_and_orientation(qapp):
    from limekit.widgets.progressbar import ProgressBar
    from PySide6.QtCore import Qt
    bar = ProgressBar()
    bar.setRange(0, 100)
    bar.setValue(50)
    assert bar.getValue() == 50
    bar.setOrientation("vertical")
    assert bar.getOrientation() == Qt.Orientation.Vertical


# -- Slider --------------------------------------------------------------

def test_slider_props_round_trip(qapp):
    from limekit.widgets.slider import Slider
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QSlider

    slider = Slider()
    slider.setRange(0, 10)
    slider.setValue(3)
    assert slider.getValue() == 3
    slider.setOrientation("vertical")
    assert slider.getOrientation() == Qt.Orientation.Vertical
    slider.setTickPosition("below")
    assert slider.getTickPosition() == QSlider.TickPosition.TicksBelow


def test_slider_onvaluechange_guarded(qapp, sink):
    from limekit.widgets.slider import Slider
    slider = Slider()
    slider.setOnValueChange(lambda *a: 1 / 0)
    slider.setValue(9)
    assert len(sink) == 1


# -- RadioButton -----------------------------------------------------------

def test_radiobutton_props_round_trip(qapp):
    from limekit.widgets.radiobutton import RadioButton
    radio = RadioButton("choice")
    assert radio.getText() == "choice"
    radio.setChecked(True)
    assert radio.isChecked() is True
    radio.setIconSize((16, 16))
    from PySide6.QtCore import QSize
    assert radio.getIconSize() == QSize(16, 16)


def test_radiobutton_onclick_guarded(qapp, sink):
    from limekit.widgets.radiobutton import RadioButton
    radio = RadioButton("choice")
    radio.setOnClick(lambda *a: 1 / 0)
    radio.click()
    assert len(sink) == 1


def test_radiobuttons_grouped_are_mutually_exclusive(qapp):
    """Also exercises ButtonGroup.addButton and its onClick event."""
    from limekit.widgets.radiobutton import RadioButton
    from limekit.widgets.buttongroup import ButtonGroup

    group = ButtonGroup()
    a, b = RadioButton("a"), RadioButton("b")
    group.addButton(a)
    group.addButton(b)
    a.setChecked(True)
    assert a.isChecked() is True
    b.setChecked(True)
    assert a.isChecked() is False               # exclusivity enforced by the group


def test_buttongroup_onclick_guarded(qapp, sink):
    from limekit.widgets.radiobutton import RadioButton
    from limekit.widgets.buttongroup import ButtonGroup

    group = ButtonGroup()
    button = RadioButton("a")
    group.addButton(button)
    group.setOnClick(lambda *a: 1 / 0)
    button.click()
    assert len(sink) == 1


# -- HLine / VLine ---------------------------------------------------------

def test_hline_and_vline_frame_shapes(qapp):
    from limekit.widgets.horizontal_line import HLine
    from limekit.widgets.vertical_line import VLine
    from PySide6.QtWidgets import QFrame

    assert HLine().frameShape() == QFrame.Shape.HLine
    assert VLine().frameShape() == QFrame.Shape.VLine


# -- Splitter ----------------------------------------------------------------

def test_splitter_props_and_children(qapp):
    from limekit.widgets.splitter import Splitter
    from limekit.widgets.button import Button
    from PySide6.QtCore import Qt

    splitter = Splitter("horizontal")
    assert splitter.getOrientation() == Qt.Orientation.Horizontal
    splitter.addChild(Button("a"))
    splitter.addChild(Button("b"))
    splitter.setHandleWidth(8)
    assert splitter.getHandleWidth() == 8
    splitter.setSizes([10, 20])
    # Qt only honours exact pane sizes once the splitter has real geometry
    # (headless/unshown widgets get an equal split instead); confirm the
    # prop round-trips the right *count* rather than pixel-perfect values.
    assert len(list(splitter.getSizes())) == 2


def test_splitter_addlayout_wraps_in_widget(qapp):
    from limekit.widgets.splitter import Splitter
    from limekit.layouts.vlayout import VLayout
    from limekit.widgets.button import Button

    splitter = Splitter()
    layout = VLayout()
    layout.addChild(Button("a"))
    assert splitter.addLayout(layout) is splitter
    assert splitter.count() == 1


# -- Scroller ----------------------------------------------------------------

def test_scroller_child_and_resizable(qapp):
    from limekit.widgets.scroller import Scroller
    from limekit.widgets.label import Label

    scroller = Scroller()
    assert scroller.isResizable() is True
    label = Label("content")
    scroller.setChild(label)
    assert scroller.getChild() is label


def test_scroller_onscroll_guarded(qapp, sink):
    from limekit.widgets.scroller import Scroller

    scroller = Scroller()
    scroller.setOnScroll(lambda *a: 1 / 0)
    scroller.verticalScrollBar().setRange(0, 100)
    scroller.verticalScrollBar().setValue(50)
    assert len(sink) == 1


# -- Registration --------------------------------------------------------

def test_tier1_widgets_are_registered(qapp):
    from limekit.kernel.registry import registry
    import limekit.widgets.lineedit, limekit.widgets.groupbox            # noqa: F401
    import limekit.layouts.formlayout, limekit.widgets.container         # noqa: F401
    import limekit.widgets.image, limekit.widgets.spinner                # noqa: F401
    import limekit.widgets.doublespinner, limekit.widgets.progressbar    # noqa: F401
    import limekit.widgets.slider, limekit.widgets.radiobutton           # noqa: F401
    import limekit.widgets.horizontal_line, limekit.widgets.vertical_line  # noqa: F401
    import limekit.widgets.splitter, limekit.widgets.scroller            # noqa: F401
    import limekit.widgets.buttongroup                                   # noqa: F401

    for path in (
        "ui.LineEdit", "ui.GroupBox", "ui.FormLayout", "ui.Container",
        "ui.Image", "ui.Spinner", "ui.DoubleSpinner", "ui.ProgressBar",
        "ui.Slider", "ui.RadioButton", "ui.HLine", "ui.VLine",
        "ui.Splitter", "ui.Scroller", "ui.ButtonGroup",
    ):
        assert registry.get(path) is not None
