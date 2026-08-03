import pytest
from PySide6.QtWidgets import QPushButton
from limekit.kernel.declarative import LimeObject
from limekit.kernel.spec import Prop
from limekit.kernel.errors import BridgeError


@pytest.fixture
def Button(qapp):
    class Button(LimeObject, QPushButton):
        text = Prop(str, default="Button", qt=("text", "setText"), coerce=str)
        flat = Prop(bool, default=False, qt=("isFlat", "setFlat"))
    return Button


def test_accessors_are_generated(Button):
    b = Button()
    assert hasattr(b, "getText") and hasattr(b, "setText")


def test_setter_does_not_recurse(Button):
    """Constraint C2: setText must call QPushButton.setText, not itself."""
    b = Button()
    b.setText("hello")
    assert b.getText() == "hello"


def test_coercion_is_applied(Button):
    b = Button()
    b.setText(42)
    assert b.getText() == "42"


def test_bool_props_get_an_is_alias(Button):
    b = Button()
    b.setFlat(True)
    assert b.isFlat() is True
    assert b.getFlat() is True


def test_validate_rejects_bad_values(qapp):
    class W(LimeObject, QPushButton):
        text = Prop(str, qt=("text", "setText"),
                    validate=lambda v: len(v) <= 3)

    w = W()
    w.setText("ok")
    with pytest.raises(BridgeError, match="text"):
        w.setText("far too long")


def test_generated_setter_returns_self_for_chaining(Button):
    b = Button()
    assert b.setText("x") is b
