import builtins

import pytest
from lupa import LuaRuntime
from PySide6.QtWidgets import QApplication

from limekit.kernel.bridge import convert
from limekit.kernel.errors import BridgeError
from limekit.services import theming
from limekit.services.theming import Theme


@pytest.fixture(scope="module", autouse=True)
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def lua():
    runtime = LuaRuntime(unpack_returned_tuples=True)
    convert.set_runtime(runtime)
    yield runtime
    convert.set_runtime(None)


def test_unknown_family_raises_bridge_error():
    with pytest.raises(BridgeError, match="unknown theme family"):
        Theme.setTheme("not-a-family", "x")


def test_get_themes_unknown_family_raises_bridge_error():
    with pytest.raises(BridgeError):
        Theme.getThemes("not-a-family")


def test_misc_get_themes_lists_bundled_qss(lua):
    names = convert.to_py(Theme.getThemes("misc"))
    assert "sublime" in names


def test_misc_set_theme_applies_stylesheet():
    Theme.setTheme("misc", "sublime")
    assert QApplication.instance().styleSheet() != ""


def test_misc_unknown_theme_name_raises_bridge_error():
    with pytest.raises(BridgeError):
        Theme.setTheme("misc", "does-not-exist")


def test_qtthemes_get_themes_lists_bundled_json(lua):
    names = convert.to_py(Theme.getThemes("qtthemes"))
    assert "nord" in names


def test_qtthemes_set_theme_applies_palette():
    Theme.setTheme("qtthemes", "nord")


def test_qtthemes_unknown_theme_raises_bridge_error():
    with pytest.raises(BridgeError):
        Theme.setTheme("qtthemes", "does-not-exist")


def test_darklight_get_themes(lua):
    assert convert.to_py(Theme.getThemes("darklight")) == ["light", "dark"]


def test_darklight_advertises_only_appliable_themes(lua):
    """Every name getThemes reports must be one setTheme accepts.

    "auto" was listed and qdarktheme's load_stylesheet rejects it, so a
    ComboBox filled from getThemes raised on that one entry.
    """
    for name in convert.to_py(Theme.getThemes("darklight")):
        assert Theme.setTheme("darklight", name) is True


def test_material_missing_package_raises_bridge_error(monkeypatch):
    real_import = builtins.__import__

    def fake_import(name, *a, **k):
        if name == "qt_material":
            raise ImportError("no module named qt_material")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(BridgeError, match="qt_material"):
        Theme.setTheme("material", "light_blue")


def test_darkstyle_missing_package_raises_bridge_error(monkeypatch):
    real_import = builtins.__import__

    def fake_import(name, *a, **k):
        if name == "qdarkstyle" or name.startswith("qdarkstyle."):
            raise ImportError("no module named qdarkstyle")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(BridgeError, match="qdarkstyle"):
        Theme.setTheme("darkstyle", "dark")


def test_set_style_unknown_raises_bridge_error():
    with pytest.raises(BridgeError):
        Theme.setStyle("not-a-real-style")


def test_get_styles_returns_a_list(lua):
    styles = convert.to_py(Theme.getStyles())
    assert isinstance(styles, list) and len(styles) > 0


def test_set_style_valid(lua):
    styles = convert.to_py(Theme.getStyles())
    assert Theme.setStyle(styles[0]) is True
