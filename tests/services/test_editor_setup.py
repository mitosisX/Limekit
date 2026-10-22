"""sys.EditorSetup: a project's .luarc.json, so editors find Limekit's API."""

import json
from pathlib import Path

from limekit.services.editor import STUBS, EditorSetup

LIBRARY = "workspace.library"


def read(project):
    return json.loads((project / ".luarc.json").read_text(encoding="utf-8"))


def test_stubs_sit_where_require_resolves():
    """require("limekit.ui") is looked up as limekit/ui.lua in each library."""
    assert (Path(STUBS) / "limekit" / "ui.lua").is_file()


def test_a_new_project_gets_a_config_pointing_at_the_stubs(tmp_path):
    assert EditorSetup.write(str(tmp_path)) is True
    config = read(tmp_path)
    assert config[LIBRARY] == [STUBS]
    assert config["runtime.version"] == "Lua 5.4"


def test_writing_again_changes_nothing(tmp_path):
    EditorSetup.write(str(tmp_path))
    before = (tmp_path / ".luarc.json").read_text(encoding="utf-8")
    assert EditorSetup.write(str(tmp_path)) is False
    assert (tmp_path / ".luarc.json").read_text(encoding="utf-8") == before


def test_a_moved_limer_has_its_old_path_replaced_and_the_rest_kept(tmp_path):
    """Unzipping Limer somewhere else must not leave a dead path behind, and
    settings the author added are theirs."""
    (tmp_path / ".luarc.json").write_text(json.dumps({
        LIBRARY: ["C:/Old/Limer/python/Lib/site-packages/limekit/runtime/lua/stubs",
                  "D:/my/own/lib"],
        "diagnostics.globals": ["love"],
    }), encoding="utf-8")

    assert EditorSetup.write(str(tmp_path)) is True
    config = read(tmp_path)
    assert config[LIBRARY] == ["D:/my/own/lib", STUBS]
    assert config["diagnostics.globals"] == ["love"]


def test_the_nested_form_is_understood_too(tmp_path):
    (tmp_path / ".luarc.json").write_text(json.dumps(
        {"workspace": {"library": ["D:/my/own/lib"]}}), encoding="utf-8")
    EditorSetup.write(str(tmp_path))
    assert read(tmp_path)["workspace"]["library"] == ["D:/my/own/lib", STUBS]


def test_a_file_it_cannot_read_is_left_alone(tmp_path):
    (tmp_path / ".luarc.json").write_text("{ not json", encoding="utf-8")
    assert EditorSetup.write(str(tmp_path)) is False
    assert (tmp_path / ".luarc.json").read_text(encoding="utf-8") == "{ not json"


def test_a_missing_folder_is_not_an_error(tmp_path):
    assert EditorSetup.write(str(tmp_path / "gone")) is False
