"""Watching a project tree: recursion, coalescing, and noise."""

import pytest
from lupa import LuaRuntime
from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWidgets import QApplication

from limekit.kernel import manifest
from limekit.kernel.bridge import convert
from limekit.kernel.errors import BridgeError
from limekit.services.watching import FileWatcher


@pytest.fixture(scope="module", autouse=True)
def qapp():
    manifest.import_all()
    return QApplication.instance() or QApplication([])


@pytest.fixture(autouse=True)
def lua():
    """The handler is handed a Lua table, so one has to exist to make."""
    runtime = LuaRuntime(unpack_returned_tuples=True)
    convert.set_runtime(runtime)
    yield runtime
    convert.set_runtime(None)


def pump(msecs):
    loop = QEventLoop()
    QTimer.singleShot(msecs, loop.quit)
    loop.exec()


@pytest.fixture
def project(tmp_path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "views").mkdir()
    (tmp_path / "misc").mkdir()
    (tmp_path / "scripts" / "main.lua").write_text("-- hi", encoding="utf-8")
    return tmp_path


def test_watching_a_tree_reaches_every_folder_beneath_it(project):
    """Qt's watcher is not recursive, which is the whole reason for this."""
    watcher = FileWatcher()
    added = watcher.watchTree(str(project))

    watched = set(watcher._watcher.directories())
    assert str(project) in watched
    assert str(project / "scripts") in watched
    assert str(project / "scripts" / "views") in watched
    assert added == 4
    watcher.clear()


def test_noise_folders_are_skipped(project):
    """A .git directory can hold more folders than the project does."""
    (project / ".git").mkdir()
    (project / "node_modules").mkdir()
    (project / "__pycache__").mkdir()

    watcher = FileWatcher()
    watcher.watchTree(str(project))
    watched = set(watcher._watcher.directories())

    assert str(project / ".git") not in watched
    assert str(project / "node_modules") not in watched
    assert str(project / "__pycache__") not in watched
    watcher.clear()


def test_watch_rejects_a_path_that_is_not_a_string():
    watcher = FileWatcher()
    with pytest.raises(BridgeError):
        watcher.watch(None)


def test_watching_something_that_does_not_exist_is_false_not_fatal(tmp_path):
    watcher = FileWatcher()
    assert watcher.watch(str(tmp_path / "nope")) is False


def test_clear_stops_watching_everything(project):
    watcher = FileWatcher()
    watcher.watchTree(str(project))
    assert watcher.getCount() > 0
    watcher.clear()
    assert watcher.getCount() == 0


def test_a_new_file_reaches_the_handler(project):
    """The thing this exists for: a file appears, the tree should know."""
    seen = []
    watcher = FileWatcher()
    watcher.setOnChange(lambda paths: seen.append(paths))
    watcher.watchTree(str(project))

    (project / "scripts" / "brand_new.lua").write_text("-- new", encoding="utf-8")
    pump(900)

    assert seen, "no change was reported"
    watcher.clear()


def test_a_file_created_in_a_nested_folder_reaches_the_handler(project):
    """The recursion is not decoration: this is where authors work."""
    seen = []
    watcher = FileWatcher()
    watcher.setOnChange(lambda paths: seen.append(paths))
    watcher.watchTree(str(project))

    (project / "scripts" / "views" / "deep.lua").write_text("-- deep", encoding="utf-8")
    pump(900)

    assert seen, "a change two folders down was missed"
    watcher.clear()


def test_a_burst_of_changes_is_reported_once(project):
    """An editor saving one file commonly produces several events."""
    seen = []
    watcher = FileWatcher()
    watcher.setOnChange(lambda paths: seen.append(paths))
    watcher.watchTree(str(project))

    for index in range(6):
        (project / "scripts" / f"file{index}.lua").write_text("--", encoding="utf-8")
    pump(900)

    assert len(seen) == 1, f"reported {len(seen)} times for one burst"
    watcher.clear()


def test_a_folder_created_after_watching_started_is_watched_too(project):
    """Otherwise the first file inside a new folder is the last one seen."""
    watcher = FileWatcher()
    watcher.setOnChange(lambda paths: None)
    watcher.watchTree(str(project))

    (project / "scripts" / "fresh").mkdir()
    pump(900)

    assert str(project / "scripts" / "fresh") in watcher._watcher.directories()
    watcher.clear()
