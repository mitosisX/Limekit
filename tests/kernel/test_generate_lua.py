import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GENERATED = REPO / "limekit" / "runtime" / "lua" / "limekit.lua"


def test_generated_lua_exists():
    assert GENERATED.is_file()


def test_generated_lua_declares_every_module():
    from limekit.kernel import manifest
    from limekit.kernel.registry import registry
    manifest.import_all()

    text = GENERATED.read_text(encoding="utf-8")
    for module in registry.modules():
        assert f'limekit.{module}' in text


def test_dead_duplicate_is_gone():
    """lua/script.py held a byte-identical copy of limekit.lua."""
    assert not (REPO / "limekit" / "lua" / "script.py").exists()


def test_regenerating_is_a_no_op():
    current = GENERATED.read_text(encoding="utf-8")
    regenerated = subprocess.run(
        [sys.executable, str(REPO / "tools" / "generate_lua.py"), "--stdout"],
        capture_output=True, text=True, check=True, cwd=REPO,
    ).stdout
    assert current.replace("\r\n", "\n") == regenerated.replace("\r\n", "\n"), (
        "limekit.lua is stale - run: python tools/generate_lua.py"
    )
