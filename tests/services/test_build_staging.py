"""What a build ships: the whole project, as source, minus what never ships."""

import os

from limekit.build.config import BuildConfig
from limekit.build.spec_generator import SpecGenerator
from limekit.build.staging import stage_project


def _project(root):
    (root / "scripts" / "build").mkdir(parents=True)            # a user module folder
    (root / "scripts" / "main.lua").write_text('print("hi")\n', encoding="utf-8")
    (root / "scripts" / "build" / "steps.lua").write_text("return {}\n", encoding="utf-8")
    (root / "images").mkdir()
    (root / "images" / "logo.png").write_bytes(b"\x89PNG")
    (root / "data").mkdir()                                      # used to be dropped
    (root / "data" / "words.csv").write_text("a,b\n", encoding="utf-8")
    (root / "notes.txt").write_text("hello", encoding="utf-8")
    (root / "app.json").write_text('{"api": "2.0"}', encoding="utf-8")
    for junk in (".git", "build", "dist", "scripts/__pycache__", "design/.preview"):
        (root / junk).mkdir(parents=True, exist_ok=True)
        (root / junk / "x").write_text("junk", encoding="utf-8")
    (root / "design" / "main.design.lua").write_text("return {}", encoding="utf-8")
    return root


def _files(root):
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())


def test_stage_project_ships_everything_but_junk(tmp_path):
    project = _project(tmp_path / "app")
    staged = tmp_path / "staged"
    stage_project(project, staged)
    assert _files(staged) == [
        "app.json",
        "data/words.csv",
        "design/main.design.lua",
        "images/logo.png",
        "notes.txt",
        "scripts/build/steps.lua",
        "scripts/main.lua",
    ]


def test_lua_ships_as_source_byte_for_byte(tmp_path):
    """No luac: bytecode under a .lua name broke the 2.0 entry point, and a
    system luac may not even be Lua 5.4."""
    project = _project(tmp_path / "app")
    staged = tmp_path / "staged"
    stage_project(project, staged)
    for name in ("scripts/main.lua", "scripts/build/steps.lua"):
        assert (staged / name).read_bytes() == (project / name).read_bytes()


def test_spec_bundles_every_staged_entry_and_parses_with_quotes_in_paths(tmp_path):
    """A path with a quote used to break the r'...' literals in the spec."""
    project = _project(tmp_path / "Bob's App")
    temp = tmp_path / "it's temp"
    temp.mkdir()
    stage_project(project, temp / "project")
    entry = temp / "app_entry.py"
    entry.write_text("", encoding="utf-8")

    config = BuildConfig()
    config.icon = str(project / "images" / "logo.png")
    spec = SpecGenerator(str(project), config, str(temp))._create_spec_content(str(entry))
    compile(spec, "<spec>", "exec")                         # it parses

    datas = {dst: src for src, dst in SpecGenerator(str(project), config, str(temp))._collect_data_files()}
    for name in ("scripts", "images", "data", "design"):
        assert repr(name) in datas
    assert repr(".") in datas                                  # top-level files


def test_a_build_leaves_no_build_folder_in_the_project(tmp_path, monkeypatch):
    """PyInstaller's work folder used to be <project>/build, left behind after
    every build. It now lives in the build's temporary folder."""
    import subprocess
    from limekit.build.builder import AppBuilder

    project = _project(tmp_path / "app")
    import shutil
    shutil.rmtree(project / "build")                 # the fixture's junk folder
    calls = []
    monkeypatch.setattr(subprocess, "run",
                        lambda args, **kw: calls.append(args) or subprocess.CompletedProcess(args, 0, "", ""))
    AppBuilder(str(project)).build()

    workpath = calls[0][calls[0].index("--workpath") + 1]
    assert not workpath.startswith(str(project))
    assert not (project / "build").exists()
