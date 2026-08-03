import pytest
from limekit.kernel.spec import Prop, Event, Method


def test_prop_records_its_attribute_name():
    class Holder:
        text = Prop(str, qt=("text", "setText"))
    assert Holder.text.name == "text"


def test_prop_accessor_names():
    p = Prop(str, qt=("text", "setText"))
    p.name = "text"
    assert p.accessor_names() == ("getText", "setText", None)


def test_bool_prop_gets_an_is_alias():
    p = Prop(bool, qt=("isFlat", "setFlat"))
    p.name = "flat"
    assert p.accessor_names() == ("getFlat", "setFlat", "isFlat")


def test_lua_name_overrides_the_generated_names():
    p = Prop(str, qt=("text", "setText"), lua_name="caption")
    p.name = "text"
    assert p.accessor_names() == ("getCaption", "setCaption", None)


def test_prop_requires_a_qt_pair():
    with pytest.raises(ValueError, match="qt"):
        Prop(str)


def test_event_setter_name():
    e = Event("clicked")
    e.name = "onClick"
    assert e.setter_name() == "setOnClick"


def test_event_defaults_to_passing_self():
    assert Event("clicked").passes_self is True


def test_method_records_its_name():
    class Holder:
        center = Method(qt="center")
    assert Holder.center.name == "center"
