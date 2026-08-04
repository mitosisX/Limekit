# tests/test_demo_smoke.py
"""Boot every demo project headless.

Demos live outside the repo, so this skips cleanly when they are absent.
Point LIMEKIT_DEMOS at the checkout to run them.

Two populations:

- `2.0-examples/*` are written against the current API and must **pass**.
  They are the working proof that the kernel produces a usable framework,
  not just a green unit suite.
- Everything else still uses the 1.x flat-global API and **xfails**. That
  count is the migration backlog, deliberately visible rather than hidden
  behind a passing suite.
"""

import os
from pathlib import Path

import pytest

DEMOS = Path(os.environ.get(
    "LIMEKIT_DEMOS",
    Path(__file__).resolve().parents[2] / "limekit-demos",
))

MODERN_DIR = "2.0-examples"


def _projects(root):
    if not root.is_dir():
        return []
    return sorted(p.parent.parent for p in root.glob("*/scripts/main.lua"))


def modern_projects():
    return _projects(DEMOS / MODERN_DIR)


def legacy_projects():
    return _projects(DEMOS)


@pytest.mark.skipif(not modern_projects(), reason="2.0-examples not found")
@pytest.mark.parametrize("project", modern_projects(), ids=lambda p: p.name)
def test_modern_demo_boots_clean(project, qapp):
    """A 2.0 example must boot with no reported errors."""
    from limekit.kernel.app import LimekitApp

    with LimekitApp(project) as app:
        app.load_project()
        assert app.errors == (), f"{project.name} reported: {app.errors}"


@pytest.mark.skipif(not modern_projects(), reason="2.0-examples not found")
def test_modern_demos_use_no_globals(qapp):
    """The 2.0 API is require-based; a bare global would be a regression.

    1.x injected ~138 names plus Python builtins. If an example can only be
    written by reaching for a global, the module story has a hole in it.
    """
    for project in modern_projects():
        source = (project / "scripts" / "main.lua").read_text(encoding="utf-8")
        assert 'require("limekit.' in source, f"{project.name} requires nothing"
        for banned in ("Window(", "VLayout(", "Button(", "Label("):
            bare = f"\n{banned}"
            assert bare not in source, (
                f"{project.name} calls a bare global {banned!r}; "
                f"use the required module table"
            )


@pytest.mark.skipif(not legacy_projects(), reason="limekit-demos checkout not found")
@pytest.mark.parametrize("project", legacy_projects(), ids=lambda p: p.name)
def test_legacy_demo_boots_without_error(project, qapp):
    from limekit.kernel.app import LimekitApp

    # These still use the 1.x flat-global API and the `app` table (theming,
    # dialogs, paths, routing), none of which the 2.0 API provides yet.
    # This suite measures the gap; it does not hide it.
    pytest.xfail(f"{project.name} uses the 1.x API - migrate in P1")

    with LimekitApp(project) as app:
        app.load_project()
        assert app.errors == (), f"{project.name} reported: {app.errors}"
