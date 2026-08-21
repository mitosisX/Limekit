"""The widget tree and property reading that the inspector channel serves."""

import pytest
from PySide6.QtWidgets import QApplication

from limekit.kernel import affinity, manifest
from limekit.services import inspect


@pytest.fixture(scope="module", autouse=True)
def qapp():
    manifest.import_all()
    return QApplication.instance() or QApplication([])


@pytest.fixture
def project(qapp):
    """A window shaped like a real main.lua: everything a local."""
    from limekit.layouts.vlayout import VLayout
    from limekit.widgets.button import Button
    from limekit.widgets.container import Container
    from limekit.widgets.label import Label
    from limekit.widgets.slider import Slider
    from limekit.widgets.window import Window

    window = Window()
    window.setTitle("Fixture")
    box, layout = Container(), VLayout()
    label, button, slider = Label("original"), Button("Press"), Slider()
    for child in (label, button, slider):
        layout.addChild(child)
    box.setLayout(layout)
    window.setMainChild(box)
    window.show()

    yield {"window": window, "label": label, "button": button, "slider": slider}

    window.close()
    affinity.forget_window(window)


def flatten(nodes):
    for node in nodes:
        yield node
        yield from flatten(node["children"])


def test_tree_finds_the_window_and_its_children(project):
    tree = inspect.tree()
    top = next(n for n in tree if n["class"] == "ui.Window")
    assert top["path"] == "1"
    assert top["label"] == "Fixture"

    classes = {n["class"] for n in flatten(tree)}
    assert {"ui.Label", "ui.Button", "ui.Slider"} <= classes


def test_every_path_in_the_tree_resolves_back_to_its_widget(project):
    """The addressing contract: a path means one widget, both ways."""
    for node in flatten(inspect.tree()):
        widget = inspect.resolve(node["path"])
        assert widget is not None, node["path"]
        assert inspect.lime_name(widget) == node["class"]


def test_resolve_returns_none_for_a_stale_path(project):
    assert inspect.resolve("9.9.9") is None
    assert inspect.resolve("") is None
    assert inspect.resolve("not.a.path") is None
    assert inspect.resolve("0") is None            # paths are 1-based


def test_a_widget_qt_made_for_itself_is_named_honestly(project):
    """A viewport or tab bar is not part of anyone's project."""
    from limekit.widgets.button import Button
    assert inspect.lime_name(Button("x")) == "ui.Button"

    from PySide6.QtWidgets import QWidget
    assert inspect.lime_name(QWidget()) == "<QWidget>"


def test_properties_are_read_from_the_registry_not_a_list(project):
    props = {p["name"]: p for p in inspect.properties(project["button"])}
    assert props["text"]["value"] == "Press"
    assert props["text"]["settable"] is True
    assert props["enabled"]["type"] == "boolean"


def test_an_object_typed_property_is_shown_but_never_edited(project):
    """An icon cannot survive a JSON round trip, so it is read-only here."""
    icon = {p["name"]: p for p in inspect.properties(project["button"])}["icon"]
    assert icon["type"] == "object"
    assert icon["settable"] is False


def test_an_enum_reads_as_its_own_name_and_offers_its_options(project):
    """A getter hands back Qt's member; nobody can type that back."""
    orientation = {p["name"]: p
                   for p in inspect.properties(project["slider"])}["orientation"]
    assert orientation["value"] == "horizontal"
    assert orientation["options"] == ["horizontal", "vertical"]


def test_setting_a_property_returns_what_it_reads_back_as(project):
    assert inspect.set_property(project["label"], "text", "changed") == "changed"
    assert project["label"].getText() == "changed"

    # Set by name, read back by name -- not as <Orientation.Vertical: 2>.
    assert inspect.set_property(project["slider"], "orientation", "vertical") == "vertical"


def test_setting_an_unknown_property_says_so(project):
    with pytest.raises(AttributeError):
        inspect.set_property(project["label"], "notAProperty", 1)
