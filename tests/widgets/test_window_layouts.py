"""Window, the layout family, and TextField.

The Window tests pin the four defects the 1.x implementation carried; each
names the defect it guards.
"""

import inspect

import pytest
from PySide6.QtCore import QPoint, QSize
from PySide6.QtGui import QContextMenuEvent, QResizeEvent

from limekit.kernel.bridge.guard import reset_error_sink, set_error_sink
from limekit.kernel.errors import BridgeError
from limekit.layouts.grid import GridLayout
from limekit.layouts.hlayout import HLayout
from limekit.layouts.vlayout import VLayout
from limekit.widgets.button import Button
from limekit.widgets.textfield import TextField
from limekit.widgets.window import Window


@pytest.fixture(autouse=True)
def sink():
    captured = []
    set_error_sink(captured.append)
    yield captured
    reset_error_sink()


def _context_event():
    return QContextMenuEvent(
        QContextMenuEvent.Reason.Mouse, QPoint(1, 1), QPoint(1, 1)
    )


# -- Window construction ---------------------------------------------------

def test_window_accepts_lua_table_style_options(qapp):
    """Lua's `Window{title=..., size={w, h}}` is a positional table call."""
    window = Window({"title": "Hello", "size": [800, 600]})
    assert window.getTitle() == "Hello"
    assert window.getSize() == (800, 600)


def test_window_accepts_python_keywords(qapp):
    window = Window(title="Hello", size=(800, 600))
    assert window.getTitle() == "Hello"


def test_window_defaults_without_options(qapp):
    assert Window().getSize() == (400, 400)


def test_window_rejects_a_malformed_size(qapp):
    with pytest.raises(BridgeError, match="size"):
        Window(size=(1, 2, 3))


# -- the four 1.x Window defects -------------------------------------------

def test_context_menu_without_a_handler_does_not_raise(qapp):
    """1.x read self.onContextMenuEvent, which was never declared."""
    Window().contextMenuEvent(_context_event())      # must not raise


def test_reshowing_does_not_recentre(qapp):
    """1.x called center() on every show, undoing the user's move."""
    window = Window()
    window.show()
    window.move(10, 10)
    window.hide()
    window.show()
    assert (window.pos().x(), window.pos().y()) == (10, 10)


def test_just_shown_flag_is_actually_used(qapp):
    """1.x declared the flag and never read it."""
    window = Window()
    assert window._just_shown is False
    window.show()
    assert window._just_shown is True


def test_close_event_calls_super(qapp):
    """1.x neither called super() nor accepted/ignored the event."""
    assert "super().closeEvent" in inspect.getsource(Window.closeEvent)


# -- Window events are guarded --------------------------------------------

def test_window_event_handlers_are_guarded(qapp, sink):
    window = Window()
    window.setOnResize(lambda *a: 1 / 0)
    window.resizeEvent(QResizeEvent(QSize(700, 600), QSize(600, 500)))
    assert len(sink) == 1


def test_context_menu_handler_is_guarded(qapp, sink):
    window = Window()
    window.setOnContextMenu(lambda *a: 1 / 0)
    window.contextMenuEvent(_context_event())
    assert len(sink) == 1


def test_window_setters_chain(qapp):
    window = Window()
    assert window.setTitle("x").setOnResize(lambda *a: None) is window


# -- layouts ---------------------------------------------------------------

@pytest.mark.parametrize("layout_cls", [VLayout, HLayout])
def test_box_layout_adds_and_counts(qapp, layout_cls):
    layout = layout_cls()
    layout.addChild(Button("a")).addChild(Button("b"))
    assert layout.getCount() == 2


@pytest.mark.parametrize("layout_cls", [VLayout, HLayout])
def test_box_layout_child_access_is_one_indexed(qapp, layout_cls):
    layout = layout_cls()
    layout.addChild(Button("first")).addChild(Button("second"))
    assert layout.getChildAt(1).getText() == "first"
    assert layout.getChildAt(2).getText() == "second"


@pytest.mark.parametrize("layout_cls", [VLayout, HLayout])
def test_box_layout_rejects_index_zero(qapp, layout_cls):
    with pytest.raises(BridgeError, match="1-indexed"):
        layout_cls().getChildAt(0)


def test_grid_is_one_indexed(qapp):
    """1.x GridLayout took raw 0-based coordinates while its siblings did not."""
    grid = GridLayout()
    grid.addChild(Button("topleft"), 1, 1)
    assert grid.getChildAt(1, 1).getText() == "topleft"


def test_grid_rejects_row_zero(qapp):
    with pytest.raises(BridgeError, match="1-indexed"):
        GridLayout().addChild(Button("x"), 0, 1)


def test_nested_layouts(qapp):
    outer, inner = VLayout(), HLayout()
    inner.addChild(Button("in"))
    outer.addLayout(inner)
    assert outer.getCount() == 1
    assert outer.getLayoutAt(1) is inner


def test_layout_clear(qapp):
    layout = VLayout()
    layout.addChild(Button("a")).addChild(Button("b"))
    assert layout.clear().getCount() == 0


def test_layout_spacing_prop(qapp):
    assert VLayout().setSpacing(12).getSpacing() == 12


def test_window_takes_a_layout(qapp):
    window, layout = Window(), VLayout()
    layout.addChild(Button("only"))
    assert window.setLayout(layout) is window


# -- TextField -------------------------------------------------------------

def test_textfield_round_trips_plain_text(qapp):
    assert TextField("hello").getText() == "hello"


def test_textfield_set_text_is_always_plain(qapp):
    """QTextEdit.setText would guess HTML; setText commits to plain text."""
    field = TextField()
    field.setText("<b>not bold</b>")
    assert field.getText() == "<b>not bold</b>"


def test_textfield_coerces_like_the_other_widgets(qapp):
    assert TextField().setText(42).getText() == "42"


def test_textfield_readonly_prop(qapp):
    field = TextField()
    field.setReadOnly(True)
    assert field.isReadOnly() is True


def test_textfield_text_change_event_is_guarded(qapp, sink):
    field = TextField()
    field.setOnTextChange(lambda *a: 1 / 0)
    field.setText("trigger")
    assert len(sink) >= 1


def test_textfield_line_count(qapp):
    assert TextField("a\nb\nc").getLineCount() == 3
