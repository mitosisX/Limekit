import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STUBS = REPO / "limekit" / "runtime" / "lua" / "stubs"


def test_a_stub_exists_per_module():
    from limekit.kernel import manifest
    from limekit.kernel.registry import registry
    manifest.import_all()
    for module in registry.modules():
        assert (STUBS / f"{module}.lua").is_file()


def test_stub_documents_generated_accessors():
    from limekit.kernel import manifest
    from limekit.kernel.registry import registry
    manifest.import_all()

    cls = registry.get("ui.Button")     # Task 16 runs first; this must exist
    text = (STUBS / "ui.lua").read_text(encoding="utf-8")
    for prop in cls.__props__:
        getter, setter, _ = prop.accessor_names()
        assert getter in text
        assert setter in text


def test_regenerating_is_a_no_op():
    before = {p.name: p.read_text(encoding="utf-8") for p in STUBS.glob("*.lua")}
    subprocess.run(
        [sys.executable, str(REPO / "tools" / "generate_stubs.py")],
        capture_output=True, text=True, check=True, cwd=REPO,
    )
    after = {p.name: p.read_text(encoding="utf-8") for p in STUBS.glob("*.lua")}
    assert before == after, "stubs are stale - run: python tools/generate_stubs.py"
