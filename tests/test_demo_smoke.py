# tests/test_demo_smoke.py
"""Boot every demo project headless.

Demos live outside the repo, so this skips cleanly when they are absent.
Point LIMEKIT_DEMOS at the checkout to run them.

Two populations:

- `2.0-examples/*` are written against the current API and must **pass**.
  They are the working proof that the kernel produces a usable framework,
  not just a green unit suite.
- Everything else is the original 1.x demo set, kept as it was. Those still
  use the flat-global API and **xfail** here: they run on the 1.x engine,
  which this test does not boot. Their subject matter has been rewritten
  against 2.0 in `2.0-examples/`, so the xfail count is a record of what the
  old engine still carries rather than a list of work outstanding.
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

    # These use the 1.x flat-global API and run on the 1.x engine, which
    # this test does not boot. They are kept as the original demo set; the
    # 2.0 rewrites live in 2.0-examples/ and are covered above.
    pytest.xfail(f"{project.name} uses the 1.x API - see 2.0-examples/")

    with LimekitApp(project) as app:
        app.load_project()
        assert app.errors == (), f"{project.name} reported: {app.errors}"


@pytest.mark.skipif(not modern_projects(), reason="2.0-examples not found")
def test_widget_gallery_covers_every_ui_class(qapp):
    """The gallery must account for every registered `ui.*` class.

    The gallery is generated from two tables in its own Lua -- widgets it
    shows live, and classes it explains it cannot show. Both are hand-written,
    so both can fall behind the framework, which is exactly what happened to
    the equivalent lists in the Limer IDE: they still advertised widgets that
    had been renamed away and missed half the ones that existed.

    The registry already knows the answer, so nothing has to be remembered:
    add a widget to `limekit.ui` and forget the gallery, and this fails.
    """
    import re

    from limekit.kernel import manifest
    from limekit.kernel.registry import registry

    gallery = DEMOS / MODERN_DIR / "widget-gallery" / "scripts" / "main.lua"
    if not gallery.is_file():
        pytest.skip("widget-gallery example not present")

    manifest.import_all()

    # Only classes the framework itself ships: the registry is a process
    # global, and other tests register throwaway classes into `ui.` that are
    # defined in the test module rather than in limekit.
    registered = {
        name for name, cls in registry.modules()["ui"].items()
        if (getattr(cls, "__module__", "") or "").startswith("limekit.")
    }

    # Both tables use the same row shape: { "ClassName", "description", ... }
    listed = set(re.findall(r'^\s*\{\s*"([A-Z]\w+)"\s*,',
                            gallery.read_text(encoding="utf-8"), re.M))

    missing = sorted(registered - listed)
    assert not missing, (
        f"widget-gallery does not mention {missing}; add each to CATALOGUE "
        f"(with a builder) or to ELSEWHERE (with where to look instead)"
    )

    stale = sorted(listed - registered)
    assert not stale, (
        f"widget-gallery lists {stale}, which limekit.ui no longer registers"
    )
