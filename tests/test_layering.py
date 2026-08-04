import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_import_contracts_hold():
    """Run the `.importlinter` contracts and assert they all pass.

    Coverage note: this only meaningfully covers the two real packages named
    in `.importlinter` -- limekit.kernel and limekit.widgets (plus
    limekit.build). It does NOT cover the legacy-tree entries in that file's
    `forbidden_modules` list (limekit.engine, .components, .utils, .gui,
    .core): those are implicit namespace packages (no __init__.py), which
    grimp cannot see, so import-linter cannot check imports against them --
    see the long comment above `forbidden_modules` in `.importlinter` for the
    experiment that proved this. The sibling test below,
    test_kernel_does_not_import_the_legacy_engine, is what actually enforces
    the legacy-tree rule. It is not redundant with this test even though it
    looks like a weaker, ad hoc check -- deleting it as "covered by
    import-linter already" would silently remove the only real enforcement
    against the kernel reaching into limekit.engine / GlobalEngine.
    """
    # Invoked by calling importlinter.cli.lint_imports() directly rather than
    # via `python -m importlinter.cli lint`: in import-linter 2.13,
    # importlinter/cli.py defines its click commands but has no `__main__`
    # guard, so `python -m importlinter.cli lint` just imports the module and
    # exits 0 WITHOUT RUNNING ANYTHING -- verified by running it against a
    # repo with no `.importlinter` file at all and observing exit 0 with no
    # output, instead of the loud "Could not read any configuration" error a
    # real run produces. If this is ever "simplified" back to
    # `python -m importlinter.cli lint`, the test will pass while checking
    # nothing. Calling lint_imports() directly is what both working console
    # scripts (`lint-imports`, `import-linter lint`) ultimately do, without
    # depending on either being on PATH.
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; from importlinter.cli import lint_imports; sys.exit(lint_imports())",
        ],
        capture_output=True, text=True, cwd=REPO,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_kernel_does_not_import_the_legacy_engine():
    """The new kernel must not reach back into the 1.x runtime.

    The legacy tree itself survives P0 so existing apps keep working; it is
    removed in P1. What matters here is that kernel/ never depends on it.
    """
    offenders = []
    for path in (REPO / "limekit" / "kernel").rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "limekit.engine" in text or "GlobalEngine" in text:
            offenders.append(path.relative_to(REPO).as_posix())
    assert offenders == [], f"kernel reaches into the legacy engine: {offenders}"
