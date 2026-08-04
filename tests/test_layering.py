import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_import_contracts_hold():
    # Invoked by calling importlinter.cli.lint_imports() directly rather than
    # via `python -m importlinter.cli lint`: importlinter.cli has no
    # `__main__` guard, so `python -m importlinter.cli ...` silently imports
    # the module and exits 0 without linting anything (verified while writing
    # this test — see task-15-report.md). Calling the function directly is
    # what both console-script entry points (`lint-imports`, `import-linter
    # lint`) ultimately do, without depending on either script being on PATH.
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
