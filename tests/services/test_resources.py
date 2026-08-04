import json

import pytest

from limekit.services import resources
from limekit.kernel.errors import BridgeError, ProjectError, RouteError


@pytest.fixture(autouse=True)
def _reset_root():
    yield
    resources._project_root = None


@pytest.fixture
def project(tmp_path):
    (tmp_path / "images").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "misc").mkdir()
    (tmp_path / "images" / "app.png").write_text("x")
    (tmp_path / "misc" / "book.txt").write_text("x")
    (tmp_path / "misc" / "hp.txt").write_text("x")
    routes = {
        "project": {
            "name": "T",
            "routes": {
                "single": {
                    "app_icon": "images::app.png",
                    "book": "misc::book.txt",
                    "broken": "misc-no-marker",
                },
                "group": {
                    "books": {
                        "Harry Potter": "misc::hp.txt",
                    },
                    "cities": {
                        "group_label": "misc",
                        "Zomba": "hp.txt",
                    },
                },
            },
        }
    }
    (tmp_path / "app.json").write_text(json.dumps(routes), encoding="utf-8")
    resources.set_project_root(tmp_path)
    return tmp_path


def test_images_scripts_misc_join_project_dirs(project):
    assert resources.Resources.images("app.png") == str(project / "images" / "app.png")
    assert resources.Resources.scripts("main.lua") == str(project / "scripts" / "main.lua")
    assert resources.Resources.misc("book.txt") == str(project / "misc" / "book.txt")


def test_using_resources_before_root_is_set_raises_project_error():
    resources._project_root = None
    with pytest.raises(ProjectError):
        resources.Resources.images("app.png")


def test_non_string_resource_name_raises_bridge_error(project):
    with pytest.raises(BridgeError):
        resources.Resources.images(None)


def test_single_route_resolves(project):
    assert resources.Resources.route("app_icon") == str(project / "images" / "app.png")
    assert resources.Resources.route("book") == str(project / "misc" / "book.txt")


def test_missing_route_key_raises_route_error_naming_the_key(project):
    with pytest.raises(RouteError, match="missing"):
        resources.Resources.route("missing")


def test_single_route_without_marker_raises_route_error(project):
    with pytest.raises(RouteError):
        resources.Resources.route("broken")


def test_group_route_resolves(project):
    assert resources.Resources.route("books::Harry Potter") == str(project / "misc" / "hp.txt")


def test_group_route_with_group_label_resolves_without_per_item_marker(project):
    # EIM: group_label = "misc" means item values are bare resource names.
    assert resources.Resources.route("cities::Zomba") == str(project / "misc" / "hp.txt")


def test_missing_group_raises_route_error(project):
    with pytest.raises(RouteError, match="nogroup"):
        resources.Resources.route("nogroup::item")


def test_missing_group_item_raises_route_error(project):
    with pytest.raises(RouteError, match="NoSuchBook"):
        resources.Resources.route("books::NoSuchBook")


def test_route_without_app_json_raises_project_error(tmp_path):
    resources.set_project_root(tmp_path)
    with pytest.raises(ProjectError):
        resources.Resources.route("anything")


def test_route_without_routes_block_raises_route_error(tmp_path):
    (tmp_path / "app.json").write_text('{"project": {"name": "T"}}', encoding="utf-8")
    resources.set_project_root(tmp_path)
    with pytest.raises(RouteError):
        resources.Resources.route("anything")


def test_unknown_marker_raises_route_error(project):
    with pytest.raises(RouteError):
        resources._resource_path("nope", "x")
