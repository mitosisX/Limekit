from PySide6.QtWidgets import QPushButton
from limekit.kernel.declarative import LimeObject
from limekit.kernel.spec import Prop, Event


def test_specs_are_collected(qapp):
    class W(LimeObject, QPushButton):
        text = Prop(str, qt=("text", "setText"))
        onClick = Event("clicked")

    assert [p.name for p in W.__props__] == ["text"]
    assert [e.name for e in W.__events__] == ["onClick"]


def test_spec_objects_are_removed_from_the_class(qapp):
    """Constraint C1: `text = Prop(...)` shadows QPushButton.text."""
    class W(LimeObject, QPushButton):
        text = Prop(str, qt=("text", "setText"))

    assert "text" not in vars(W)
    assert callable(W().text)          # QPushButton.text resurfaced


def test_subclasses_inherit_parent_specs(qapp):
    class Base(LimeObject, QPushButton):
        text = Prop(str, qt=("text", "setText"))

    class Child(Base):
        flat = Prop(bool, qt=("isFlat", "setFlat"))

    assert {p.name for p in Child.__props__} == {"text", "flat"}


def test_subclass_may_override_a_parent_prop(qapp):
    class Base(LimeObject, QPushButton):
        text = Prop(str, qt=("text", "setText"), doc="base")

    class Child(Base):
        text = Prop(str, qt=("text", "setText"), doc="child")

    docs = {p.name: p.doc for p in Child.__props__}
    assert docs["text"] == "child"
    assert len(Child.__props__) == 1        # overridden, not duplicated


def test_overriding_does_not_corrupt_the_parent(qapp):
    class Base(LimeObject, QPushButton):
        text = Prop(str, qt=("text", "setText"), doc="base")

    class Child(Base):
        text = Prop(str, qt=("text", "setText"), doc="child")

    assert {p.doc for p in Base.__props__} == {"base"}


def test_lime_path_is_recorded(qapp):
    class W(LimeObject, QPushButton):
        __lime__ = "ui.Thing"

    assert W.__lime__ == "ui.Thing"
