"""ProjectRunner and ProjectBuilder (`limekit.services.projects`).

The 2.0 replacements for 1.x's `app.runProject` / `app.buildProject` -- the
two globals that had no 2.0 equivalent, and so the two things blocking Limer
from being ported.

Nothing here spawns a real child process: a build takes minutes and produces
a 50MB executable. What is worth testing is the wiring -- engine detection,
the guard on every callback, and that the 1.x binding still exposes the same
surface after the logic moved out from under it.
"""

import json

import pytest

from limekit.kernel.bridge import convert
from limekit.kernel.bridge.guard import reset_error_sink, set_error_sink
from limekit.kernel.errors import BridgeError
from limekit.kernel.registry import registry
from limekit.services.projects import ProjectBuilder, ProjectRunner


@pytest.fixture(autouse=True)
def sink():
    captured = []
    set_error_sink(captured.append)
    yield captured
    reset_error_sink()


@pytest.fixture
def lua():
    """`getOutput` returns a Lua table, so it needs a runtime bound."""
    from lupa import LuaRuntime
    runtime = LuaRuntime(unpack_returned_tuples=True)
    convert.set_runtime(runtime)
    yield runtime
    convert.set_runtime(None)


def _project(tmp_path, *, api=None, main="print('hi')"):
    (tmp_path / "scripts").mkdir(exist_ok=True)
    (tmp_path / "scripts" / "main.lua").write_text(main, encoding="utf-8")
    app_json = {"project": {"name": "t"}}
    if api is not None:
        app_json["api"] = api
    (tmp_path / "app.json").write_text(json.dumps(app_json), encoding="utf-8")
    return str(tmp_path)


# -- registration -------------------------------------------------------------

def test_both_services_are_registered():
    assert registry.get("sys.ProjectRunner") is ProjectRunner
    assert registry.get("sys.ProjectBuilder") is ProjectBuilder


# -- ProjectRunner ------------------------------------------------------------

def test_runner_reports_the_project_path(qapp, tmp_path):
    path = _project(tmp_path)
    runner = ProjectRunner(path)
    assert runner.getPath() == path
    assert runner.isRunning() is False


@pytest.mark.parametrize("api, main, expected", [
    ("2.0", "print('hi')", "2.0"),                 # explicit declaration wins
    ("1.0", 'require("limekit.ui")', "1.0"),       # ...even against the sniff
    (None, 'require("limekit.ui")', "2.0"),        # structural fallback
    (None, "print('hi')", "1.0"),                  # ambiguous means 1.x
])
def test_runner_detects_the_engine(qapp, tmp_path, api, main, expected):
    runner = ProjectRunner(_project(tmp_path, api=api, main=main))
    assert runner.getApiVersion() == expected


def test_runner_rejects_a_non_path(qapp):
    with pytest.raises(BridgeError):
        ProjectRunner(None)
    with pytest.raises(BridgeError):
        ProjectRunner("")


def test_runner_callbacks_are_guarded(qapp, tmp_path, sink):
    runner = ProjectRunner(_project(tmp_path))

    assert runner.setOnProcessReadyRead(lambda output: 1 / 0) is runner
    assert runner.setOnProcessStarted(lambda: 1 / 0) is runner
    assert runner.setOnProcessFinished(lambda: 1 / 0) is runner

    # Fire them the way the QProcess signals would, without a real process.
    runner._process.onProcessReadyRead("some output")
    runner._process.onProcessStarted()
    runner._process.onProcessFinished()

    assert len(sink) == 3
    assert {e.widget for e in sink} == {"ProjectRunner"}
    assert {e.event for e in sink} == {
        "onProcessReadyRead", "onProcessStarted", "onProcessFinished",
    }


# -- ProjectBuilder -----------------------------------------------------------

def test_builder_defaults_before_a_build(qapp, tmp_path, lua):
    builder = ProjectBuilder(_project(tmp_path))
    assert builder.isSuccess() is False
    assert builder.getOutputPath() is None
    assert list(builder.getOutput().values()) == []


def test_builder_accepts_an_options_table(qapp, tmp_path):
    builder = ProjectBuilder(_project(tmp_path), {"console": True, "name": "App"})
    assert builder._process.options["console"] is True
    assert builder._process.options["name"] == "App"


def test_builder_without_options_is_fine(qapp, tmp_path):
    assert ProjectBuilder(_project(tmp_path))._process.options == {}


def test_builder_callbacks_are_guarded(qapp, tmp_path, sink):
    builder = ProjectBuilder(_project(tmp_path))

    assert builder.setOnBuildOutput(lambda line: 1 / 0) is builder
    assert builder.setOnBuildStarted(lambda: 1 / 0) is builder
    assert builder.setOnBuildFinished(lambda ok, path: 1 / 0) is builder
    assert builder.setOnBuildError(lambda message: 1 / 0) is builder

    builder._process.onBuildOutput("compiling")
    builder._process.onBuildStarted()
    builder._process.onBuildFinished(True, "dist/app.exe")
    builder._process.onBuildError("boom")

    assert len(sink) == 4
    assert {e.widget for e in sink} == {"ProjectBuilder"}


class _FakeStdout:
    """Stands in for the QProcess, so the real _handleStdout path can run."""

    def __init__(self, *chunks):
        self._chunks = list(chunks)

    def readAllStandardOutput(self):
        payload = self._chunks.pop(0).encode("utf-8")
        return type("_Bytes", (), {"data": lambda _self, p=payload: p})()


def test_builder_parses_the_build_result_line(qapp, tmp_path, lua):
    """The child prints BUILD_RESULT:<json>; that is what sets success/path."""
    builder = ProjectBuilder(_project(tmp_path))
    process = builder._process

    payload = json.dumps({"success": True, "message": "ok",
                          "output_path": "dist/app.exe"})
    process.process = _FakeStdout("Compiling Lua scripts...",
                                  "BUILD_RESULT:" + payload)

    process._handleStdout()           # ordinary output
    assert builder.isSuccess() is False

    process._handleStdout()           # the result line
    assert builder.isSuccess() is True
    assert builder.getOutputPath() == "dist/app.exe"
    assert "Compiling Lua scripts..." in list(builder.getOutput().values())


def test_builder_survives_a_malformed_result_line(qapp, tmp_path, lua):
    """A truncated result must not take the build process down with it."""
    builder = ProjectBuilder(_project(tmp_path))
    process = builder._process
    process.process = _FakeStdout("BUILD_RESULT:{not json")

    process._handleStdout()           # logs a warning, does not raise

    assert builder.isSuccess() is False
    assert builder.getOutputPath() is None


# -- the 1.x binding still works ----------------------------------------------

def test_legacy_project_builder_keeps_its_surface(qapp):
    """The 1.x `__appBuild` global is Limer's Build button today.

    Its logic moved to build/runner.BuildProcess; this guards against the
    move quietly dropping a method Limer calls.
    """
    from limekit.build.project_builder import ProjectBuilder as Legacy

    assert Legacy.name == "__appBuild"
    for expected in ("setOnBuildOutput", "setOnBuildStarted", "setOnBuildFinished",
                     "setOnBuildError", "build", "stop", "getOutput",
                     "isSuccess", "getOutputPath"):
        assert callable(getattr(Legacy, expected)), expected


def test_legacy_subprocess_runner_shim_still_exports(qapp):
    """1.x imports these from core/bootstrap; they live in limekit.launcher now."""
    from limekit.core.bootstrap import subprocess_runner as shim
    from limekit import launcher

    assert shim.detect_api_version is launcher.detect_api_version
    assert shim.ProjectRunner is launcher.ProjectRunner
    assert shim.LEGACY_ENTRY == ("-c", "from limekit import runner")
    assert shim.MODERN_ENTRY == ("-m", "limekit")
