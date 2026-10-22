"""One engine: 2.0 projects run and build; 1.x projects are refused, plainly.

The 1.x engine was retired. A 1.x project is still recognised, so that both
Run and Build can say why it will not work instead of starting it and
letting it die on its first flat global (`attempt to call a nil value
(global 'Window')`), which reads like the user's mistake rather than ours.
"""

import json

import pytest

from limekit.build.builder import AppBuilder
from limekit.build.entry_script import EntryScriptGenerator
from limekit.launcher import ENTRY, UNSUPPORTED_1X, ProjectRunner, detect_api_version

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


def test_explicit_api_field_can_mark_1x(tmp_path):
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


def test_a_1x_project_is_recognised(tmp_path):
    project = make_project(tmp_path, LEGACY_MAIN, {"project": {"name": "old"}})
    assert detect_api_version(project) == "1.0"


def test_missing_project_reads_as_1x(tmp_path):
    assert detect_api_version(tmp_path / "nope") == "1.0"


def test_malformed_app_json_falls_back_instead_of_raising(tmp_path):
    project = make_project(tmp_path, LEGACY_MAIN)
    (project / "app.json").write_text("{ not json", encoding="utf-8")
    assert detect_api_version(project) == "1.0"


def test_malformed_app_json_still_allows_structural_detection(tmp_path):
    project = make_project(tmp_path, MODERN_MAIN)
    (project / "app.json").write_text("{ not json", encoding="utf-8")
    assert detect_api_version(project) == "2.0"


# -- run -------------------------------------------------------------------

def test_every_project_runs_on_the_one_entry(qapp, tmp_path):
    project = make_project(tmp_path, MODERN_MAIN, {"api": "2.0"})
    assert ENTRY == ("-m", "limekit")
    assert ProjectRunner(str(project)).command()[2:4] == list(ENTRY)


def test_running_a_1x_project_says_why_and_starts_nothing(qapp, tmp_path):
    from PySide6.QtCore import QProcess
    project = make_project(tmp_path, LEGACY_MAIN)
    runner = ProjectRunner(str(project))
    said, finished = [], []
    runner.setOnProcessReadyRead(said.append)
    runner.setOnProcessFinished(lambda code, crashed: finished.append((code, crashed)))
    runner.run()
    assert said == [UNSUPPORTED_1X]
    assert finished == [(1, False)]
    assert runner.state() == QProcess.ProcessState.NotRunning


# -- build -----------------------------------------------------------------

def test_building_a_1x_project_is_refused_with_the_same_reason(tmp_path):
    project = make_project(tmp_path / "proj", LEGACY_MAIN, {"project": {"name": "Old"}})
    success, message, output = AppBuilder(str(project)).build()
    assert (success, message, output) == (False, UNSUPPORTED_1X, None)


def test_the_entry_script_is_the_2_0_one(tmp_path):
    script = EntryScriptGenerator(str(tmp_path)).generate()
    text = open(script, encoding="utf-8").read()
    assert "LimekitApp" in text
    assert "limekit.runner" not in text
