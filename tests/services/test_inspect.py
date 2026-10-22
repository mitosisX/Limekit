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


def test_a_widget_is_named_by_its_limekit_class_never_by_qt(project):
    """No Qt class name reaches the person looking: a widget Limekit did not
    build is named after the Limekit class nearest to what it is."""
    from limekit.widgets.button import Button
    assert inspect.lime_name(Button("x")) == "ui.Button"

    from PySide6.QtWidgets import QDialog, QLabel, QWidget
    assert inspect.lime_name(QLabel("x")) == "ui.Label"
    assert inspect.lime_name(QDialog()) == "ui.Modal"
    assert inspect.lime_name(QWidget()) == "ui.Container"


@pytest.fixture
def busy(qapp):
    """Widgets Qt fills with parts of its own: a spinner's text box, a
    list's viewport and scroll bars, a scroller's viewport, a form's row
    labels, a tab's bar."""
    from limekit.layouts.formlayout import FormLayout
    from limekit.layouts.vlayout import VLayout
    from limekit.widgets.container import Container
    from limekit.widgets.label import Label
    from limekit.widgets.listbox import ListBox
    from limekit.widgets.scroller import Scroller
    from limekit.widgets.spinner import Spinner
    from limekit.widgets.tab import Tab
    from limekit.widgets.window import Window

    window = Window()
    window.setTitle("Busy")
    box, layout = Container(), VLayout()

    form_box, form = Container(), FormLayout()
    form.addChild("Count", Spinner())
    form_box.setLayout(form)

    scroller, inside = Scroller(), Label("scrolled")
    scroller.setChild(inside)

    tab = Tab()
    tab.addTab(ListBox(), "List")

    for child in (form_box, scroller, tab):
        layout.addChild(child)
    box.setLayout(layout)
    window.setMainChild(box)
    window.show()

    yield {"window": window, "inside": inside}

    window.close()
    affinity.forget_window(window)


def test_the_tree_holds_only_limekit_widgets(busy):
    nodes = [n for n in flatten(inspect.tree()) if n["path"].startswith("1")]
    classes = {n["class"] for n in nodes}
    assert {"ui.Spinner", "ui.ListBox", "ui.Scroller", "ui.Tab"} <= classes
    for node in nodes:
        assert node["class"].startswith("ui."), node


def test_a_widget_inside_qt_parts_sits_under_its_limekit_parent(busy):
    """A scroller's content lives in Qt's viewport; the tree skips the
    viewport and the path still finds the content."""
    nodes = list(flatten(inspect.tree()))
    scroller = next(n for n in nodes if n["class"] == "ui.Scroller")
    assert [c["label"] for c in scroller["children"]] == ["scrolled"]
    assert inspect.resolve(scroller["children"][0]["path"]) is busy["inside"]

    for node in nodes:
        assert inspect.lime_name(inspect.resolve(node["path"])) == node["class"]


def test_a_form_row_titled_with_text_gets_a_limekit_label(busy):
    labels = {n["label"] for n in flatten(inspect.tree()) if n["class"] == "ui.Label"}
    assert "Count" in labels


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
    assert "Q" not in str(icon["value"]) and "PySide" not in str(icon["value"])


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
