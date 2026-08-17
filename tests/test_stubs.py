"""The generated Lua Language Server stubs must be valid Lua.

They are never executed, so nothing at runtime notices when they are not --
but the language server parses each file as a whole and discards it entirely
on a syntax error, silently taking every class in that module's autocomplete
with it.

This caught a real one: several methods take a parameter named `end`
(`setRange(self, start, end)`), which is a Lua reserved word, so `ui.lua` and
`chart.lua` both failed to parse -- roughly 70 classes' worth of completion,
gone, with no symptom anywhere else.
"""

import pathlib

import pytest
from lupa import LuaRuntime

STUBS = sorted((pathlib.Path(__file__).resolve().parent.parent
                / "limekit" / "runtime" / "lua" / "stubs").glob("*.lua"))


def test_stubs_exist():
    assert STUBS, "no stub files found; run tools/generate_stubs.py"


@pytest.mark.parametrize("path", STUBS, ids=lambda p: p.name)
def test_stub_is_valid_lua(path):
    runtime = LuaRuntime()
    source = path.read_text(encoding="utf-8")
    try:
        runtime.compile(source)
    except Exception as exc:                                # noqa: BLE001
        pytest.fail(f"{path.name} is not valid Lua: {exc}")


@pytest.mark.parametrize("path", STUBS, ids=lambda p: p.name)
def test_stub_avoids_lua_keywords_as_parameters(path):
    """A clearer failure than the parse error, pointing at the actual cause."""
    from tools.generate_stubs import LUA_KEYWORDS

    import re
    offenders = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^function [\w.:]+\(([^)]*)\)", line)
        if not match:
            continue
        for param in (p.strip() for p in match.group(1).split(",")):
            if param in LUA_KEYWORDS:
                offenders.append(f"{line}  (parameter {param!r})")
    assert not offenders, "reserved word used as a parameter name:\n" + "\n".join(offenders)
