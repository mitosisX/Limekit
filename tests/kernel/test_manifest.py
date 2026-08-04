# tests/kernel/test_manifest.py
import subprocess
import sys
from pathlib import Path

from limekit.kernel import manifest

REPO = Path(__file__).resolve().parents[2]


def test_manifest_is_non_empty():
    assert len(manifest.MODULES) > 0


def test_every_listed_module_is_importable():
    import importlib
    for name in manifest.MODULES:
        importlib.import_module(name)


def test_import_all_populates_the_registry():
    from limekit.kernel.registry import registry
    manifest.import_all()
    registered = {cls.__lime__ for cls in registry.all()}
    assert registered, "import_all() registered nothing"
    # Every listed module must contribute at least one registered class.
    assert len(registered) >= len(manifest.MODULES)


def test_regenerating_the_manifest_is_a_no_op():
    """The check that would have caught the frozen-mode divergence."""
    current = (REPO / "limekit" / "kernel" / "manifest.py").read_text(encoding="utf-8")
    regenerated = subprocess.run(
        [sys.executable, str(REPO / "tools" / "generate_manifest.py"), "--stdout"],
        capture_output=True, text=True, check=True, cwd=REPO,
    ).stdout
    assert current.replace("\r\n", "\n") == regenerated.replace("\r\n", "\n"), (
        "manifest.py is stale - run: python tools/generate_manifest.py"
    )
