"""Running and building must pick the same engine for a given project.

Limer -- the tool people actually use to run and ship Limekit apps -- calls
`app.runProject` and `app.buildProject`, which land in `ProjectRunner.run`
and `EntryScriptGenerator.generate`. Both hardcoded the 1.x entry point, so a
2.0 project died at startup with:

    module 'limekit.ui' not found: no field package.preload['limekit.ui']

because the 1.x engine injects flat globals and never populates
package.preload. These tests pin the dispatch, and pin that Run and Build
agree -- a project that runs but will not build is worse than one that does
neither, because the failure surfaces at ship time.
"""

import json

import pytest

from limekit.build.entry_script import EntryScriptGenerator
from limekit.core.bootstrap.subprocess_runner import (
    LEGACY_ENTRY,
    MODERN_ENTRY,
    detect_api_version,
)

MODERN_MAIN = 'local ui = require("limekit.ui")\nui.Window{title="x"}\n'
LEGACY_MAIN = 'window = Window{title="x"}\nwindow:show()\n'


def make_project(tmp_path, main_lua, app_json=None):
    (tmp_path / "scripts").mkdir(parents=True, exist_ok=True)
    (tmp_path / "scripts" / "main.lua").write_text(main_lua, encoding="utf-8")
    if app_json is not None:
        (tmp_path / "app.json").write_text(json.dumps(app_json), encoding="utf-8")
    return tmp_path


# -- detection -------------------------------------------------------------

def test_explicit_api_field_wins(tmp_path):
    project = make_project(tmp_path, LEGACY_MAIN, {"api": "2.0"})
    assert detect_api_version(project) == "2.0"


def test_explicit_api_field_can_force_legacy(tmp_path):
    """An explicit 1.0 must beat the structural signal, not lose to it."""
    project = make_project(tmp_path, MODERN_MAIN, {"api": "1.0"})
    assert detect_api_version(project) == "1.0"


def test_requiring_a_limekit_module_implies_2_0(tmp_path):
    project = make_project(tmp_path, MODERN_MAIN)
    assert detect_api_version(project) == "2.0"


@pytest.mark.parametrize("quote", ['"', "'"])
def test_both_lua_quote_styles_are_detected(tmp_path, quote):
    source = f"local ui = require({quote}limekit.ui{quote})\n"
    assert detect_api_version(make_project(tmp_path, source)) == "2.0"


def test_a_1x_project_stays_1x(tmp_path):
    """The ~52 existing demos must not be dragged onto the new engine."""
    project = make_project(tmp_path, LEGACY_MAIN, {"project": {"name": "old"}})
    assert detect_api_version(project) == "1.0"


def test_missing_project_defaults_to_legacy(tmp_path):
    assert detect_api_version(tmp_path / "nope") == "1.0"


def test_malformed_app_json_falls_back_instead_of_raising(tmp_path):
    project = make_project(tmp_path, LEGACY_MAIN)
    (project / "app.json").write_text("{ not json", encoding="utf-8")
    assert detect_api_version(project) == "1.0"


def test_malformed_app_json_still_allows_structural_detection(tmp_path):
    project = make_project(tmp_path, MODERN_MAIN)
    (project / "app.json").write_text("{ not json", encoding="utf-8")
    assert detect_api_version(project) == "2.0"


# -- run dispatch ----------------------------------------------------------

def test_entry_points_are_distinct():
    assert LEGACY_ENTRY != MODERN_ENTRY
    assert MODERN_ENTRY == ("-m", "limekit")


# -- build dispatch --------------------------------------------------------

def test_build_emits_the_modern_entry_for_a_2_0_project(tmp_path):
    project = make_project(tmp_path / "proj", MODERN_MAIN, {"api": "2.0"})
    out = tmp_path / "out"
    out.mkdir()
    script = EntryScriptGenerator(str(out), str(project)).generate()
    text = open(script, encoding="utf-8").read()
    assert "LimekitApp" in text
    assert "from limekit.runner import" not in text


def test_build_emits_the_legacy_entry_for_a_1x_project(tmp_path):
    project = make_project(tmp_path / "proj", LEGACY_MAIN)
    out = tmp_path / "out"
    out.mkdir()
    script = EntryScriptGenerator(str(out), str(project)).generate()
    text = open(script, encoding="utf-8").read()
    assert "from limekit.runner import LimerApplication" in text
    assert "LimekitApp" not in text


def test_build_without_a_project_keeps_the_legacy_default(tmp_path):
    """Any caller not yet passing a project must behave exactly as before."""
    script = EntryScriptGenerator(str(tmp_path)).generate()
    assert "from limekit.runner import LimerApplication" in open(
        script, encoding="utf-8"
    ).read()


@pytest.mark.parametrize("main_lua,expected", [
    (MODERN_MAIN, "2.0"),
    (LEGACY_MAIN, "1.0"),
])
def test_run_and_build_never_disagree(tmp_path, main_lua, expected):
    """The whole point: one project, one engine, both code paths."""
    project = make_project(tmp_path / "proj", main_lua)
    out = tmp_path / "out"
    out.mkdir()

    detected = detect_api_version(project)
    script = EntryScriptGenerator(str(out), str(project)).generate()
    built_modern = "LimekitApp" in open(script, encoding="utf-8").read()

    assert detected == expected
    assert built_modern is (detected == "2.0")
