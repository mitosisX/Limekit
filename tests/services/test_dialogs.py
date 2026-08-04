import pytest
from lupa import LuaRuntime
from PySide6.QtWidgets import (
    QApplication, QColorDialog, QFileDialog, QFontDialog, QInputDialog,
    QMessageBox,
)
from PySide6.QtGui import QColor, QFont

from limekit.kernel.bridge import convert
from limekit.kernel.errors import BridgeError
from limekit.services.dialogs import Dialogs


@pytest.fixture(scope="module", autouse=True)
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def lua():
    runtime = LuaRuntime(unpack_returned_tuples=True)
    convert.set_runtime(runtime)
    yield runtime
    convert.set_runtime(None)


def test_alert_does_not_raise(monkeypatch):
    monkeypatch.setattr(QMessageBox, "exec", lambda self: QMessageBox.StandardButton.Ok)
    assert Dialogs.alert(None, "Title", "Message") is None


def test_question_returns_true_on_yes(monkeypatch):
    monkeypatch.setattr(QMessageBox, "exec", lambda self: QMessageBox.StandardButton.Yes)
    assert Dialogs.question(None, "Title", "Message?") is True


def test_question_returns_false_on_no(monkeypatch):
    monkeypatch.setattr(QMessageBox, "exec", lambda self: QMessageBox.StandardButton.No)
    assert Dialogs.question(None, "Title", "Message?") is False


def test_text_input_returns_value_on_accept(monkeypatch):
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("typed", True))
    assert Dialogs.textInput(None, "Title", "Label") == "typed"


def test_text_input_returns_none_on_cancel(monkeypatch):
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("", False))
    assert Dialogs.textInput(None, "Title", "Label") is None


def test_multiline_input_returns_none_on_cancel(monkeypatch):
    monkeypatch.setattr(QInputDialog, "getMultiLineText", lambda *a, **k: ("", False))
    assert Dialogs.multilineInput(None, "Title", "Label") is None


def test_combo_box_input_returns_value(monkeypatch):
    monkeypatch.setattr(QInputDialog, "getItem", lambda *a, **k: ("b", True))
    assert Dialogs.comboBoxInput(None, "Title", "Label", ["a", "b", "c"], 2) == "b"


def test_combo_box_input_returns_none_on_cancel(monkeypatch):
    monkeypatch.setattr(QInputDialog, "getItem", lambda *a, **k: ("", False))
    assert Dialogs.comboBoxInput(None, "Title", "Label", ["a", "b"]) is None


def test_combo_box_input_requires_items():
    with pytest.raises(BridgeError):
        Dialogs.comboBoxInput(None, "Title", "Label", [])


def test_integer_input_returns_none_on_cancel(monkeypatch):
    monkeypatch.setattr(QInputDialog, "getInt", lambda *a, **k: (0, False))
    assert Dialogs.integerInput(None, "Title", "Label") is None


def test_integer_input_returns_value(monkeypatch):
    monkeypatch.setattr(QInputDialog, "getInt", lambda *a, **k: (7, True))
    assert Dialogs.integerInput(None, "Title", "Label", value=1) == 7


def test_double_input_returns_none_on_cancel(monkeypatch):
    monkeypatch.setattr(QInputDialog, "getDouble", lambda *a, **k: (0.0, False))
    assert Dialogs.doubleInput(None, "Title", "Label") is None


def test_open_file_returns_none_on_cancel(monkeypatch):
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: ("", ""))
    assert Dialogs.openFile(None) is None


def test_open_file_returns_path(monkeypatch):
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: ("/a/b.txt", ""))
    assert Dialogs.openFile(None, filters={"Text": ["txt"]}) == "/a/b.txt"


def test_save_file_returns_none_on_cancel(monkeypatch):
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: ("", ""))
    assert Dialogs.saveFile(None) is None


def test_pick_folder_returns_none_on_cancel(monkeypatch):
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: "")
    assert Dialogs.pickFolder(None) is None


def test_pick_colour_returns_none_on_cancel(monkeypatch, lua):
    monkeypatch.setattr(QColorDialog, "getColor", lambda *a, **k: QColor())
    assert Dialogs.pickColour(None) is None


def test_pick_colour_returns_table_on_accept(monkeypatch, lua):
    monkeypatch.setattr(QColorDialog, "getColor", lambda *a, **k: QColor(10, 20, 30))
    result = convert.to_py(Dialogs.pickColour(None))
    assert result["r"] == 10 and result["g"] == 20 and result["b"] == 30


def test_pick_font_returns_none_on_cancel(monkeypatch):
    monkeypatch.setattr(QFontDialog, "getFont", lambda *a, **k: (QFont(), False))
    assert Dialogs.pickFont(None) is None


def test_pick_font_returns_table_on_accept(monkeypatch, lua):
    monkeypatch.setattr(QFontDialog, "getFont", lambda *a, **k: (QFont("Arial", 12), True))
    result = convert.to_py(Dialogs.pickFont(None))
    assert result["family"] == "Arial"
    assert result["pointSize"] == 12
