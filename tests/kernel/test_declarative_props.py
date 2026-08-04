import pytest
from PySide6.QtWidgets import QPushButton
from limekit.kernel.declarative import LimeObject
from limekit.kernel.spec import Prop
from limekit.kernel.errors import BridgeError, RegistryError


@pytest.fixture
def Button(qapp):
    class Button(LimeObject, QPushButton):
        text = Prop(str, qt=("text", "setText"), coerce=str)
        flat = Prop(bool, qt=("isFlat", "setFlat"))
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


def test_inherited_prop_setter_does_not_double_wrap(qapp):
    """A prop declared on Base must not accumulate wrapper layers when
    re-installed on each subclass down a multi-level inheritance chain.
    Each generation's _install_prop call must resolve past the previous
    generation's generated setter to find the real Qt method."""
    calls = []

    def counting_coerce(v):
        calls.append(v)
        return str(v)

    class Base(LimeObject, QPushButton):
        text = Prop(str, qt=("text", "setText"), coerce=counting_coerce)

    class Mid(Base):
        pass

    class Leaf(Mid):
        pass

    for cls in (Base, Mid, Leaf):
        calls.clear()
        w = cls()
        w.setText("x")
        assert calls == ["x"], (
            f"{cls.__name__}: coerce should fire exactly once per call, "
            f"got {len(calls)} calls: {calls}"
        )


def test_abstract_mixin_prop_installs_on_concrete_subclass(qapp):
    """A mixin like LimeWidget may declare props whose Qt methods only exist
    on a concrete Qt widget. Defining the mixin itself must not raise, and a
    concrete subclass combining the mixin with a real widget must get
    working accessors."""

    class LimeWidget(LimeObject):
        enabled = Prop(bool, qt=("isEnabled", "setEnabled"))

    # The mixin itself has no isEnabled/setEnabled anywhere in its MRO, so
    # accessors must not be installed on it -- but defining it must not raise.
    assert not hasattr(LimeWidget, "getEnabled")
    assert not hasattr(LimeWidget, "setEnabled")

    class Widget(LimeWidget, QPushButton):
        pass

    w = Widget()
    w.setEnabled(False)
    assert w.getEnabled() is False
    assert w.isEnabled() is False


def test_prop_colliding_with_an_unrelated_qt_method_raises(qapp):
    """A Prop whose generated accessor name collides with an unrelated Qt
    method must not silently replace it. fixedSize's generated setFixedSize
    would otherwise call resize() instead of Qt's own setFixedSize."""
    with pytest.raises(RegistryError, match="setFixedSize"):
        class Widget(LimeObject, QPushButton):
            fixedSize = Prop(object, qt=("size", "resize"))


def test_prop_colliding_with_a_hand_written_method_raises(qapp):
    """The ComboBox.getText shape: a hand-written method must not be
    silently replaced by a generated accessor of the same name."""
    with pytest.raises(RegistryError, match="getText"):
        class Widget(LimeObject, QPushButton):
            text = Prop(str, qt=("text", "setText"), coerce=str)

            def getText(self):
                return "hand-written"


def test_diamond_inheritance_collects_props_from_all_branches(qapp):
    """Two mixins declaring different props, combined via diamond
    inheritance, must both end up on the leaf class -- the ancestor-tuple
    collector merge (reversed MRO) must not drop either branch."""

    class Base(LimeObject, QPushButton):
        text = Prop(str, qt=("text", "setText"), coerce=str)

    class LeftMixin(Base):
        flat = Prop(bool, qt=("isFlat", "setFlat"))

    class RightMixin(Base):
        checkable = Prop(bool, qt=("isCheckable", "setCheckable"))

    class Leaf(LeftMixin, RightMixin):
        pass

    names = {p.name for p in Leaf.__props__}
    assert {"text", "flat", "checkable"} <= names

    w = Leaf()
    w.setText("hi")
    w.setFlat(True)
    w.setCheckable(True)
    assert w.getText() == "hi"
    assert w.isFlat() is True
    assert w.isCheckable() is True
