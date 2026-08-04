"""Theming exposed to Lua as `require("limekit.ui").Theme`.

Ports limekit/core/theming/themes/themer.py and its five theme families (1.x)
to the 2.0 service-layer pattern. Several families depend on optional
third-party packages (qt_material, qdarktheme, qdarkstyle); 1.x silently
no-op'd with a printed warning when one was missing. That silent failure is
exactly the sort of defect this migration is meant to fix -- a Lua script
setting a theme that quietly does nothing is much harder to debug than one
that raises. Here a missing optional dependency raises BridgeError naming
the package to install, instead.
"""

import json
import os

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from limekit.kernel.bridge.convert import to_lua
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError

_QTTHEMES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "limekit", "core", "theming", "themes", "qtthemes", "themes",
)
_MISC_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "limekit", "core", "theming", "themes", "misc", "themes",
)

_QTTHEMES_COLOR_KEYS = (
    "primary", "secondary", "magenta", "red", "orange", "yellow", "green",
    "cyan", "blue", "text", "subtext1", "subtext0", "overlay2", "overlay1",
    "overlay0", "surface2", "surface1", "surface0", "base", "mantle", "crust",
)


def _app():
    app = QApplication.instance()
    if app is None:
        raise BridgeError("no QApplication is running; ui.Theme requires a booted app")
    return app


# -- material -----------------------------------------------------------

def _set_material(name):
    try:
        from qt_material import apply_stylesheet
    except ImportError as exc:
        raise BridgeError(
            "the 'qt_material' package is not installed; install it with "
            "'pip install qt-material' to use the material theme family"
        ) from exc
    try:
        apply_stylesheet(_app(), f"{name}.xml")
    except Exception as exc:                                # noqa: BLE001
        raise BridgeError(f"could not apply material theme {name!r}: {exc}") from exc


def _themes_material():
    try:
        from qt_material import list_themes
    except ImportError:
        return []
    return [theme.rsplit(".", 1)[0] for theme in list_themes()]


# -- misc (qss stylesheets) ----------------------------------------------

def _set_misc(name):
    path = os.path.join(_MISC_DIR, f"{name.lower()}.qss")
    if not os.path.isfile(path):
        raise BridgeError(f"unknown misc theme {name!r}: no file at {path}")
    try:
        content = open(path, encoding="utf-8").read()
    except OSError as exc:
        raise BridgeError(f"could not read theme {name!r}: {exc}") from exc
    _app().setStyleSheet(content)


def _themes_misc():
    if not os.path.isdir(_MISC_DIR):
        return []
    return sorted(
        f.rsplit(".qss", 1)[0].lower()
        for f in os.listdir(_MISC_DIR) if f.endswith(".qss")
    )


# -- darklight (qdarktheme) ----------------------------------------------

def _set_darklight(name):
    try:
        import qdarktheme
    except ImportError as exc:
        raise BridgeError(
            "the 'pyqtdarktheme' package is not installed; install it with "
            "'pip install pyqtdarktheme' to use the darklight theme family"
        ) from exc
    try:
        stylesheet = qdarktheme.load_stylesheet(name)
    except Exception as exc:                                # noqa: BLE001
        raise BridgeError(f"could not apply darklight theme {name!r}: {exc}") from exc
    _app().setStyleSheet(stylesheet)


def _themes_darklight():
    return ["light", "dark", "auto"]


# -- darkstyle (qdarkstyle) ------------------------------------------------

def _set_darkstyle(name):
    try:
        import qdarkstyle
        from qdarkstyle.dark.palette import DarkPalette
        from qdarkstyle.light.palette import LightPalette
    except ImportError as exc:
        raise BridgeError(
            "the 'qdarkstyle' package is not installed; install it with "
            "'pip install qdarkstyle' to use the darkstyle theme family"
        ) from exc
    palette = DarkPalette if name == "dark" else LightPalette
    _app().setStyleSheet(qdarkstyle.load_stylesheet(palette=palette))


def _themes_darkstyle():
    try:
        import qdarkstyle  # noqa: F401
    except ImportError:
        return []
    return ["dark", "light"]


# -- qtthemes (bundled JSON palettes) --------------------------------------

def _load_qtthemes_palette(name):
    path = os.path.join(_QTTHEMES_DIR, f"{name}.json")
    if not os.path.isfile(path):
        raise BridgeError(f"unknown qtthemes theme {name!r}: no file at {path}")
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise BridgeError(f"could not read theme {name!r}: {exc}") from exc
    missing = [key for key in _QTTHEMES_COLOR_KEYS if key not in data]
    if missing:
        raise BridgeError(f"theme {name!r} is missing colors: {', '.join(missing)}")
    return {key: QColor(data[key]) for key in _QTTHEMES_COLOR_KEYS}


def _set_qtthemes(name):
    colors = _load_qtthemes_palette(name)
    is_dark = colors["text"].value() > colors["base"].value()

    palette = QPalette()
    Role = QPalette.ColorRole
    Group = QPalette.ColorGroup

    if is_dark:
        palette.setColor(Role.Base, colors["mantle"])
        palette.setColor(Role.AlternateBase, colors["base"])
    else:
        palette.setColor(Role.Base, colors["crust"])
        palette.setColor(Role.AlternateBase, colors["mantle"])
    palette.setColor(Role.Window, colors["base"])
    palette.setColor(Role.WindowText, colors["text"])
    palette.setColor(Role.Text, colors["text"])
    palette.setColor(Role.Button, colors["base"])
    palette.setColor(Role.ButtonText, colors["text"])
    palette.setColor(Role.ToolTipBase, colors["mantle"])
    palette.setColor(Role.ToolTipText, colors["overlay2"])
    palette.setColor(Role.Highlight, colors["primary"])
    palette.setColor(Role.Link, colors["secondary"])
    palette.setColor(Group.Disabled, Role.WindowText, colors["overlay1"])
    palette.setColor(Group.Disabled, Role.Text, colors["overlay1"])
    palette.setColor(Group.Disabled, Role.ButtonText, colors["overlay1"])

    app = _app()
    app.setStyle("fusion")
    app.setPalette(palette)


def _themes_qtthemes():
    if not os.path.isdir(_QTTHEMES_DIR):
        return []
    return sorted(
        f.rsplit(".json", 1)[0]
        for f in os.listdir(_QTTHEMES_DIR) if f.endswith(".json")
    )


_FAMILIES = {
    "material": (_set_material, _themes_material),
    "misc": (_set_misc, _themes_misc),
    "darklight": (_set_darklight, _themes_darklight),
    "darkstyle": (_set_darkstyle, _themes_darkstyle),
    "qtthemes": (_set_qtthemes, _themes_qtthemes),
}


class Theme(LimeObject):
    __lime__ = "ui.Theme"

    @staticmethod
    def setTheme(family, name):
        if not isinstance(family, str) or family.lower() not in _FAMILIES:
            raise BridgeError(
                f"unknown theme family {family!r}; expected one of: "
                f"{', '.join(sorted(_FAMILIES))}"
            )
        if not isinstance(name, str) or not name:
            raise BridgeError(f"expected a non-empty theme name, got {name!r}")
        setter, _ = _FAMILIES[family.lower()]
        setter(name)
        return True

    @staticmethod
    def getThemes(family):
        if not isinstance(family, str) or family.lower() not in _FAMILIES:
            raise BridgeError(
                f"unknown theme family {family!r}; expected one of: "
                f"{', '.join(sorted(_FAMILIES))}"
            )
        _, lister = _FAMILIES[family.lower()]
        return to_lua(lister())

    @staticmethod
    def setStyle(name):
        if not isinstance(name, str) or not name:
            raise BridgeError(f"expected a non-empty style name, got {name!r}")
        from PySide6.QtWidgets import QStyleFactory
        available = QStyleFactory.keys()
        if name not in available:
            raise BridgeError(
                f"unknown style {name!r}; expected one of: {', '.join(available)}"
            )
        _app().setStyle(name)
        return True

    @staticmethod
    def getStyles():
        from PySide6.QtWidgets import QStyleFactory
        return to_lua(list(QStyleFactory.keys()))
