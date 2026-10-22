"""The child-process build: the script it generates, and what it reports."""

import sys
import types

import pytest

from limekit.build.runner import BuildProcess, _build_script


def _run_script(script, monkeypatch, outcome=(True, "ok", "dist/App.exe")):
    """Execute a generated build script against a stand-in AppBuilder."""
    seen = {}

    class FakeBuilder:
        def __init__(self, project_path, output_dir, options):
            seen.update(project_path=project_path, output_dir=output_dir, options=options)

        def build(self, console_mode):
            seen["console_mode"] = console_mode
            return outcome

    fake = types.ModuleType("limekit.build.builder")
    fake.AppBuilder = FakeBuilder
    monkeypatch.setitem(sys.modules, "limekit.build.builder", fake)
    exec(compile(script, "<build script>", "exec"), {})
    return seen


def test_paths_with_quotes_and_backslashes_reach_the_builder_intact(monkeypatch, capsys):
    """A folder named "Bob's App" used to produce a script that would not parse."""
    path = "C:\\Users\\bob\\Bob's App\\it's here"
    out = "C:\\out\\O'Neil"
    options = {"name": "Bob's \"App\"", "icon": "C:\\icons\\it's.png", "console": True}
    seen = _run_script(_build_script(path, options, True, out), monkeypatch)
    assert seen["project_path"] == path
    assert seen["output_dir"] == out
    assert seen["options"] == {"name": "Bob's \"App\"", "icon": "C:\\icons\\it's.png"}
    assert seen["console_mode"] is True


def test_no_output_dir_is_none(monkeypatch, capsys):
    seen = _run_script(_build_script("C:\\p", {}, False, None), monkeypatch)
    assert seen["output_dir"] is None


class _FakeProcess:
    def __init__(self, stdout=b"", stderr=b""):
        self._out, self._err = stdout, stderr

    def readAllStandardOutput(self):
        return types.SimpleNamespace(data=lambda: self._out)

    def readAllStandardError(self):
        return types.SimpleNamespace(data=lambda: self._err)


def _reporting(stdout):
    build = BuildProcess("C:\\p")
    errors = []
    build.setOnBuildError(errors.append)
    build.process = _FakeProcess(stdout=stdout)
    build._handleStdout()
    return build, errors


def test_build_error_printed_on_stdout_reaches_onbuilderror():
    """The script prints BUILD_ERROR to stdout; only stderr was ever read."""
    _, errors = _reporting(b"Compiling...\nBUILD_ERROR:PyInstaller is not installed\n")
    assert errors == ["PyInstaller is not installed"]


def test_a_failed_build_reaches_onbuilderror_with_its_message():
    result = b'BUILD_RESULT:{"success": false, "message": "Project validation failed", "output_path": null}'
    build, errors = _reporting(result)
    assert errors == ["Project validation failed"]
    assert build.isSuccess() is False


def test_a_successful_build_reports_no_error():
    result = b'Done\nBUILD_RESULT:{"success": true, "message": "ok", "output_path": "dist/App.exe"}\n'
    build, errors = _reporting(result)
    assert errors == []
    assert build.isSuccess() is True
    assert build.getOutputPath() == "dist/App.exe"


@pytest.mark.parametrize("onefile", [True, False])
def test_the_single_file_choice_reaches_the_builder(monkeypatch, capsys, onefile):
    """Unticking "Pack into a single file" still built a single file: the
    option was never forwarded, and False would have been dropped anyway."""
    seen = _run_script(_build_script("C:\p", {"onefile": onefile}, False, None), monkeypatch)
    assert seen["options"]["onefile"] is onefile


def test_no_single_file_choice_leaves_the_default(monkeypatch, capsys):
    seen = _run_script(_build_script("C:\p", {}, False, None), monkeypatch)
    assert "onefile" not in seen["options"]
