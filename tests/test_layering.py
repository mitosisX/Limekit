import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_import_contracts_hold():
    """Run the `.importlinter` contracts and assert they all pass.

    The kernel imports nothing from the rest of limekit, and widgets sit
    above the kernel. See `.importlinter`.
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


# The 1.x engine was retired: these were its packages, and its runner.
RETIRED = ("engine", "components", "core", "utils", "gui", "lua", "config")


def test_the_1x_engine_stays_retired():
    """Nothing of the 1.x engine remains, and nothing reaches for it.

    It was half the codebase and only ran 1.x projects; a 1.x project is now
    recognised and refused (`launcher.detect_api_version`). An import of one
    of its modules would fail only when that code path ran -- this fails now.
    """
    package = REPO / "limekit"
    assert [n for n in RETIRED if (package / n).exists()] == []
    assert not (package / "runner.py").exists()

    # Anchored to the start of a line: a real import, not a comment quoting one.
    pattern = re.compile(r"^\s*(?:from|import)\s+limekit\.(?:%s|runner)\b" % "|".join(RETIRED),
                         re.MULTILINE)
    offenders = [p.relative_to(REPO).as_posix() for p in package.rglob("*.py")
                 if pattern.search(p.read_text(encoding="utf-8", errors="ignore"))]
    assert offenders == [], f"code still imports the 1.x engine: {offenders}"
