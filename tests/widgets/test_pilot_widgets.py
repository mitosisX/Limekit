import pytest
from limekit.kernel.bridge.guard import set_error_sink, reset_error_sink


@pytest.fixture(autouse=True)
def sink():
    captured = []
    set_error_sink(captured.append)
    yield captured
    reset_error_sink()


def test_button_text_round_trips(qapp):
    from limekit.widgets.button import Button
    assert Button("hi").getText() == "hi"


def test_checkbox_coerces_like_button(qapp):
    """CheckBox.setText used to skip the str() that Button applied."""
    from limekit.widgets.button import Button
    from limekit.widgets.checkbox import CheckBox
    assert Button().setText(42).getText() == CheckBox().setText(42).getText() == "42"


def test_listbox_accepts_a_python_list(qapp):
    """ListBox.setItems called .values() unconditionally and crashed on this."""
    from limekit.widgets.listbox import ListBox
    box = ListBox()
    box.setItems(["a", "b"])
    assert box.getItemsCount() == 2


def test_combobox_and_listbox_agree_on_setItems(qapp):
    from limekit.widgets.listbox import ListBox
    from limekit.widgets.combobox import ComboBox
    ListBox().setItems(["a", "b"])
    ComboBox().setItems(["a", "b"])          # neither may raise


def test_every_widget_shares_one_resize_rule(qapp):
    """BaseWidget had 7 size policies; ComboBox re-declared only 3."""
    from limekit.widgets.combobox import ComboBox
    from limekit.widgets.button import Button
    for widget in (ComboBox(), Button()):
        widget.setResizeRule("minimumexpanding", "preferred")


def test_combobox_callbacks_are_guarded(qapp, sink):
    """Only Button used to guard its callbacks."""
    from limekit.widgets.combobox import ComboBox
    box = ComboBox()
    box.setOnItemSelect(lambda *a: 1 / 0)
    box.setItems(["a", "b"])
    box.setCurrentIndex(1)
    assert len(sink) >= 1


def test_label_cursor_map_is_correct(qapp):
    from limekit.widgets.label import Label
    from PySide6.QtCore import Qt
    label = Label("x")
    label.setCursor("wait")
    assert label.cursor().shape() == Qt.CursorShape.WaitCursor
    label.setCursor("openhand")
    assert label.cursor().shape() == Qt.CursorShape.OpenHandCursor


def test_widgets_are_registered(qapp):
    from limekit.kernel.registry import registry
    import limekit.widgets.button, limekit.widgets.label          # noqa: F401
    import limekit.widgets.checkbox, limekit.widgets.listbox      # noqa: F401
    import limekit.widgets.combobox                               # noqa: F401
    for path in ("ui.Button", "ui.Label", "ui.CheckBox", "ui.ListBox", "ui.ComboBox"):
        assert registry.get(path) is not None
