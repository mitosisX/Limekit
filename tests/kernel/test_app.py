import pytest

from limekit.kernel.app import LimekitApp
from limekit.kernel.errors import ProjectError


@pytest.fixture
def project(tmp_path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "main.lua").write_text(
        'local ui = require("limekit.ui")\nRAN = true\n', encoding="utf-8"
    )
    (tmp_path / "app.json").write_text('{"project": {"name": "T"}}', encoding="utf-8")
    return tmp_path


def test_importing_limekit_has_no_side_effects():
    """A fresh interpreter must not construct a QApplication on import."""
    import subprocess, sys
    code = (
        "import limekit, limekit.kernel.app;"
        "from PySide6.QtWidgets import QApplication;"
        "print(QApplication.instance() is None)"
    )
    out = subprocess.run([sys.executable, "-c", code],
                         capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "True"


def test_boot_creates_a_runtime(project):
    app = LimekitApp(project)
    app.boot()
    assert app.runtime is not None
    app.shutdown()


def test_load_project_executes_main_lua(project):
    app = LimekitApp(project)
    app.boot()
    app.load_project()
    assert app.runtime.eval("RAN") is True
    app.shutdown()


def test_missing_main_lua_raises_project_error(tmp_path):
    (tmp_path / "scripts").mkdir()
    app = LimekitApp(tmp_path)
    app.boot()
    with pytest.raises(ProjectError, match="main.lua"):
        app.load_project()
    app.shutdown()


def test_context_manager_shuts_down(project):
    with LimekitApp(project) as app:
        app.load_project()
        assert app.runtime is not None
    assert app.runtime is None
