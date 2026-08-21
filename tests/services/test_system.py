import base64

import pytest
from lupa import LuaRuntime
from PySide6.QtWidgets import QApplication

from limekit.kernel.bridge import convert
from limekit.kernel.errors import BridgeError
from limekit.services.system import System


@pytest.fixture(scope="module", autouse=True)
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def lua():
    runtime = LuaRuntime(unpack_returned_tuples=True)
    convert.set_runtime(runtime)
    yield runtime
    convert.set_runtime(None)


def test_execute_returns_stdout(lua):
    result = convert.to_py(System.execute("echo hello"))
    assert "hello" in result["stdout"]
    assert result["returncode"] == 0


def test_execute_rejects_empty_command():
    with pytest.raises(BridgeError):
        System.execute("")


def test_execute_times_out_is_a_bridge_error(lua, monkeypatch):
    import subprocess

    def fake_run(*a, **k):
        raise subprocess.TimeoutExpired(cmd="sleep 100", timeout=1)

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(BridgeError, match="timed out"):
        System.execute("sleep 100")


def test_get_os_name_is_a_string():
    assert isinstance(System.getOSName(), str)


def test_get_cpu_count_is_positive():
    assert System.getCPUCount() > 0


def test_sleep_rejects_negative():
    with pytest.raises(BridgeError):
        System.sleep(-1)


def test_sleep_accepts_non_numeric_raises_bridge_error():
    with pytest.raises(BridgeError):
        System.sleep("nope")


def test_clipboard_round_trip():
    System.setClipboardText("hello clipboard")
    assert System.getClipboardText() == "hello clipboard"


def test_set_clipboard_rejects_non_string():
    with pytest.raises(BridgeError):
        System.setClipboardText(123)


def test_split_string(lua):
    assert convert.to_py(System.splitString("a,b,c", ",")) == ["a", "b", "c"]


def test_random_choice_from_list():
    assert System.randomChoice(["a"]) == "a"


def test_random_choice_empty_raises_bridge_error():
    with pytest.raises(BridgeError):
        System.randomChoice([])


def test_make_hash_md5():
    assert System.makeHash("md5", "hello") == "5d41402abc4b2a76b9719d911017c592"


def test_make_hash_unknown_algorithm_raises_bridge_error():
    with pytest.raises(BridgeError):
        System.makeHash("not-a-hash", "hello")


def test_base64_round_trip():
    encoded = System.toBase64("hello")
    assert encoded == base64.b64encode(b"hello").decode("ascii")
    assert System.fromBase64(encoded) == "hello"


def test_from_base64_invalid_raises_bridge_error():
    with pytest.raises(BridgeError):
        System.fromBase64("not valid base64!!")


def test_bytes_to_readable_size():
    assert System.bytesToReadableSize(500) == "500 B"
    assert System.bytesToReadableSize(2048) == "2.00 KB"


def test_bytes_to_readable_size_rejects_negative():
    with pytest.raises(BridgeError):
        System.bytesToReadableSize(-1)


def test_emoji_missing_package_raises_bridge_error(monkeypatch):
    import builtins
    real_import = builtins.__import__

    def fake_import(name, *a, **k):
        if name == "emoji":
            raise ImportError("no module named emoji")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(BridgeError, match="emoji"):
        System.emoji(":thumbs_up:")


def test_get_standard_path_unknown_name_raises_bridge_error():
    with pytest.raises(BridgeError):
        System.getStandardPath("not-a-real-location")


def test_get_standard_path_documents_returns_a_string():
    assert isinstance(System.getStandardPath("documents"), str)


def test_open_path_rejects_empty():
    with pytest.raises(BridgeError):
        System.openPath("")


def test_open_path_rejects_non_string():
    with pytest.raises(BridgeError):
        System.openPath(None)


def test_open_path_hands_an_existing_file_to_the_desktop_as_a_local_url(tmp_path, monkeypatch):
    target = tmp_path / "main.lua"
    target.write_text("-- hi", encoding="utf-8")

    seen = []
    monkeypatch.setattr(
        "PySide6.QtGui.QDesktopServices.openUrl",
        lambda url: seen.append(url) or True,
    )

    assert System.openPath(str(target)) is True
    assert seen[0].isLocalFile()
    assert seen[0].toLocalFile().endswith("main.lua")


def test_open_path_treats_a_non_existent_path_as_a_url(monkeypatch):
    seen = []
    monkeypatch.setattr(
        "PySide6.QtGui.QDesktopServices.openUrl",
        lambda url: seen.append(url) or True,
    )

    System.openPath("https://limekit.dev")
    assert seen[0].isLocalFile() is False
    assert seen[0].toString() == "https://limekit.dev"
