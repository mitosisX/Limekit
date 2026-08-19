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


def test_a_shown_window_survives_a_lua_collection(qapp, tmp_path):
    """A Lua chunk's locals die with the chunk.

    Every example ends `window:show()` and then falls off the end of
    main.lua, at which point the only reference to the window is a local in
    a finished chunk. Before the framework held one of its own, a single
    `collectgarbage("collect")` left a booted application with no top-level
    widgets at all -- and, running for real, the app simply exited.
    """
    from PySide6.QtWidgets import QApplication

    from limekit.kernel.app import LimekitApp

    project = tmp_path / "app"
    (project / "scripts").mkdir(parents=True)
    (project / "app.json").write_text(
        '{"api": "2.0", "project": {"name": "x", "version": "1", '
        '"author": "x", "description": "x"}}', encoding="utf-8")
    (project / "scripts" / "main.lua").write_text(
        'local ui = require("limekit.ui")\n'
        'local window = ui.Window { title = "held" }\n'
        'window:show()\n', encoding="utf-8")

    def titles():
        return [w.windowTitle() for w in QApplication.topLevelWidgets()
                if w.metaObject().className() == "Window"]

    with LimekitApp(project) as app:
        app.load_project()
        assert "held" in titles()

        app.runtime.execute("collectgarbage('collect') collectgarbage('collect')")
        assert "held" in titles(), "the window was collected once main.lua returned"


def test_closing_a_window_lets_it_go(qapp, tmp_path):
    """The other half: holding a reference for ever would leak every window
    an application ever showed."""
    from limekit.kernel import affinity
    from limekit.kernel.app import LimekitApp

    project = tmp_path / "app"
    (project / "scripts").mkdir(parents=True)
    (project / "app.json").write_text(
        '{"api": "2.0", "project": {"name": "x", "version": "1", '
        '"author": "x", "description": "x"}}', encoding="utf-8")
    (project / "scripts" / "main.lua").write_text(
        'local ui = require("limekit.ui")\n'
        '_G.win = ui.Window { title = "temporary" }\n'
        '_G.win:show()\n', encoding="utf-8")

    with LimekitApp(project) as app:
        app.load_project()
        assert len(affinity._windows) == 1
        app.runtime.execute("_G.win:close()")
        assert len(affinity._windows) == 0
