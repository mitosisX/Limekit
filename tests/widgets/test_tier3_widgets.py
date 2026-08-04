"""Tier-3 widgets: pickers, knob, advanced slider, accordion, gif player,
sliding stack, stacked layout, LCD number, font combo box, command button,
spacer, separator.

Mirrors the conventions in test_pilot_widgets.py / test_tier2_widgets.py.
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


# -- Calendar / DatePicker / TimePicker --------------------------------------

def test_calendar_date_round_trips(qapp):
    from limekit.widgets.calendar import Calendar
    cal = Calendar()
    assert cal.setDate(2024, 5, 1) is cal
    assert cal.getDate() == "2024-5-1"
    assert cal.setGridVisible(True) is cal
    assert cal.isGridVisible() is True


def test_calendar_ondatepicked_guarded(qapp, sink):
    from limekit.widgets.calendar import Calendar
    cal = Calendar()
    cal.setOnDatePicked(lambda *a: 1 / 0)
    cal._handleDateClicked(cal.selectedDate())
    assert len(sink) == 1


def test_datepicker_date_round_trips(qapp):
    from limekit.widgets.datepicker import DatePicker
    picker = DatePicker()
    assert picker.setDate(2024, 5, 1) is picker
    assert picker.getDate() == "2024-5-1"


def test_timepicker_time_round_trips(qapp):
    from limekit.widgets.timepicker import TimePicker
    picker = TimePicker()
    assert picker.setTime(13, 5, 9) is picker
    assert picker.getTime() == "13:5:9"


# -- Knob ---------------------------------------------------------------

def test_knob_value_and_range(qapp):
    from limekit.widgets.knob import Knob
    knob = Knob()
    assert knob.setRange(0, 100) is knob
    assert knob.setValue(50) is knob
    assert knob.getValue() == 50


def test_knob_onvaluechanged_fires(qapp):
    from limekit.widgets.knob import Knob
    knob = Knob()
    knob.setRange(0, 100)
    seen = []
    knob.setOnValueChanged(lambda self, value: seen.append(value))
    knob.setValue(60)
    assert seen == [60]


# -- AdvancedSlider -----------------------------------------------------

def test_advanced_slider_value_round_trips(qapp):
    from limekit.widgets.advancedslider import AdvancedSlider
    slider = AdvancedSlider()
    assert slider.setRange(0, 100) is slider
    assert slider.setValue(42) is slider
    assert slider.getValue() == 42


def test_advanced_slider_colours_accept_strings(qapp):
    from limekit.widgets.advancedslider import AdvancedSlider
    slider = AdvancedSlider()
    assert slider.setTextColor("#ff0000") is slider
    assert slider.setBackgroundColor("#00ff00") is slider
    assert slider.getTextColor().name() == "#ff0000"


def test_advanced_slider_onvaluechanged_fires(qapp):
    from limekit.widgets.advancedslider import AdvancedSlider
    slider = AdvancedSlider()
    slider.setRange(0, 100)
    seen = []
    slider.setOnValueChanged(lambda self, value: seen.append(value))
    slider.setValue(10)
    assert seen == [10]


def test_advanced_slider_float_formatting(qapp):
    from limekit.widgets.advancedslider import AdvancedSlider
    slider = AdvancedSlider()
    slider.setRange(0, 10)
    slider.setFloat(True)
    slider.setDecimals(2)
    slider.setValue(3.14159)
    assert slider.getValue() == 3.14
    assert "3.14" in slider.getValueFormatted()


# -- Accordion ------------------------------------------------------------

def test_accordion_addchild_and_current_index(qapp):
    from limekit.widgets.accordion import Accordion
    from limekit.widgets.button import Button

    acc = Accordion()
    assert acc.addChild(Button("a"), "First") is acc
    acc.addChild(Button("b"), "Second")
    assert acc.getCount() == 2
    assert acc.setCurrentIndex(1) is acc
    assert acc.getCurrentIndex() == 1


def test_accordion_oncurrentchange_guarded(qapp, sink):
    from limekit.widgets.accordion import Accordion
    from limekit.widgets.button import Button

    acc = Accordion()
    acc.addChild(Button("a"), "a")
    acc.addChild(Button("b"), "b")
    acc.setOnCurrentChange(lambda *a: 1 / 0)
    acc.setCurrentIndex(1)
    assert len(sink) == 1


# -- GifPlayer ------------------------------------------------------------

def test_gifplayer_state_and_frame_accessors(qapp, tmp_path):
    from limekit.widgets.gifplayer import GifPlayer
    # A real (if empty/invalid) file path is enough: QMovie degrades
    # gracefully rather than raising, and the surface under test is the
    # Lua-facing accessors, not GIF decoding itself.
    player = GifPlayer(str(tmp_path / "missing.gif"))
    assert player.getState() in ("notrunning", "paused", "running")
    # An invalid/missing file makes QMovie report -1 ("unknown") rather than
    # raising; the accessor itself is what is under test here.
    assert player.getFramesCount() >= -1
    assert player.getCurrentFrame() >= 0          # 1-indexed (Qt's -1 "unknown" + 1)


# -- SlidingStackedWidget -------------------------------------------------

def test_sliding_stacked_widget_add_and_count(qapp):
    from limekit.widgets.slidingstackedwidget import SlidingStackedWidget
    from limekit.widgets.button import Button

    stack = SlidingStackedWidget()
    assert stack.addChild(Button("a")) is stack
    stack.addChild(Button("b"))
    assert stack.getCount() == 2


def test_sliding_stacked_widget_unknown_animation_raises_bridge_error(qapp):
    from limekit.widgets.slidingstackedwidget import SlidingStackedWidget
    stack = SlidingStackedWidget()
    with pytest.raises(BridgeError):
        stack.setAnimation("not-a-real-curve")


# -- StackedLayout --------------------------------------------------------

def test_stacked_layout_add_and_current_index(qapp):
    from limekit.layouts.stackedlayout import StackedLayout
    from limekit.widgets.button import Button

    layout = StackedLayout()
    assert layout.addChild(Button("a")) is layout
    layout.addChild(Button("b"))
    assert layout.getCount() == 2
    assert layout.setCurrentIndex(2) is layout
    assert layout.getCurrentIndex() == 2

    with pytest.raises(BridgeError):
        layout.setCurrentIndex(0)              # 1-indexed, 0 is out of range


# -- LCDNumber --------------------------------------------------------------

def test_lcdnumber_value_and_digit_count(qapp):
    from limekit.widgets.lcdnumber import LCDNumber
    lcd = LCDNumber()
    assert lcd.setValue(42) is lcd
    assert lcd.getValue() == 42.0
    assert lcd.setDigitCount(5) is lcd
    assert lcd.getDigitCount() == 5


# -- FontComboBox -----------------------------------------------------------

def test_fontcombobox_add_and_select(qapp):
    from limekit.widgets.fontcombobox import FontComboBox
    combo = FontComboBox()
    assert combo.addItem("Arial") is combo
    assert combo.getText()


def test_fontcombobox_onitemselect_guarded(qapp, sink):
    from limekit.widgets.fontcombobox import FontComboBox
    combo = FontComboBox()
    combo.addItems(["Arial", "Courier"])
    combo.setOnItemSelect(lambda *a: 1 / 0)
    combo.setCurrentIndex(2)
    assert len(sink) == 1


# -- CommandButton ------------------------------------------------------

def test_commandbutton_text_and_description(qapp):
    from limekit.widgets.commandbutton import CommandButton
    button = CommandButton("Title")
    assert button.getText() == "Title"
    assert button.setDescription("more info") is button
    assert button.getDescription() == "more info"


def test_commandbutton_onclick_fires(qapp):
    from limekit.widgets.commandbutton import CommandButton
    button = CommandButton("Title")
    clicked = []
    button.setOnClick(lambda self: clicked.append(1))
    button.click()
    assert clicked == [1]


# -- Spacer / Separator ---------------------------------------------------

def test_spacer_constructs(qapp):
    from limekit.widgets.spacer import Spacer
    Spacer(10, 20)                              # must not raise


def test_separator_orientations(qapp):
    from limekit.widgets.separator import Separator
    from PySide6.QtWidgets import QFrame
    assert Separator("horizontal").frameShape() == QFrame.Shape.HLine
    assert Separator("vertical").frameShape() == QFrame.Shape.VLine


def test_separator_unknown_orientation_raises_bridge_error(qapp):
    from limekit.widgets.separator import Separator
    with pytest.raises(BridgeError):
        Separator("diagonal")
