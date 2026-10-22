"""The entry point a built 2.0 app starts from."""

import pytest

from limekit.build.entry_script import EntryScriptGenerator


def _run_entry(tmp_path, main_lua, monkeypatch):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "main.lua").write_text(main_lua, encoding="utf-8")
    (tmp_path / "app.json").write_text('{"api": "2.0", "project": {"name": "Demo"}}',
                                       encoding="utf-8")
    entry = tmp_path / "app_entry.py"
    entry.write_text(EntryScriptGenerator.ENTRY_SCRIPT_TEMPLATE, encoding="utf-8")

    shown = []
    from PySide6.QtWidgets import QMessageBox
    monkeypatch.setattr(QMessageBox, "critical",
                        staticmethod(lambda parent, title, text: shown.append((title, text))))
    with pytest.raises(SystemExit) as exited:
        exec(compile(entry.read_text(encoding="utf-8"), str(entry), "exec"),
             {"__file__": str(entry), "__name__": "__main__"})
    return exited.value.code, shown


def test_a_lua_error_at_startup_is_shown_not_swallowed(qapp, tmp_path, monkeypatch):
    """A windowed build has no console: the app used to just vanish."""
    code, shown = _run_entry(tmp_path, 'local x = 1\nerror("no config file")\n', monkeypatch)
    assert code == 1
    assert len(shown) == 1
    title, text = shown[0]
    assert "no config file" in text
    assert "scripts/main.lua" in text and "2" in text     # where it happened
