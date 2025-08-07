from __future__ import annotations

import dataclasses
import importlib.resources
import json
import logging
import os
from json import JSONDecodeError
from limekit.engine.lifecycle.app import App
from PySide6 import QtGui, QtWidgets
from limekit.utils.converters import Converter

# import qt_themes

ColorGroup = QtGui.QPalette.ColorGroup
ColorRole = QtGui.QPalette.ColorRole

THEMES = "QT_THEMES"
PROPERTY_NAME = "theme"

logger = logging.getLogger(__package__)


@dataclasses.dataclass
class Theme:
    primary: QtGui.QColor | None = None
    secondary: QtGui.QColor | None = None

    magenta: QtGui.QColor | None = None
    red: QtGui.QColor | None = None
    orange: QtGui.QColor | None = None
    yellow: QtGui.QColor | None = None
    green: QtGui.QColor | None = None
    cyan: QtGui.QColor | None = None
    blue: QtGui.QColor | None = None

    text: QtGui.QColor | None = None
    subtext1: QtGui.QColor | None = None
    subtext0: QtGui.QColor | None = None
    overlay2: QtGui.QColor | None = None
    overlay1: QtGui.QColor | None = None
    overlay0: QtGui.QColor | None = None
    surface2: QtGui.QColor | None = None
    surface1: QtGui.QColor | None = None
    surface0: QtGui.QColor | None = None
    base: QtGui.QColor | None = None
    mantle: QtGui.QColor | None = None
    crust: QtGui.QColor | None = None

    def is_dark_theme(self) -> bool:
        return self.text.value() > self.base.value()


class QtThemes:

    def __init__(self):
        self.app = App.app
        self.dir_path = os.path.abspath(os.path.dirname(__file__))
        self.themes_path = os.path.join(self.dir_path, "themes")
        self.all_themes = os.listdir(self.themes_path)

    def getTheme(self, name: str | None = None) -> Theme | None:
        """
        Return the theme with `name` if found and valid.

        If no name is provided, return the current theme applied to the QApplication. This
        only works in the same Python session.
        """

        if name is None:
            return

        file_name = f"{name}.json"
        for theme in self.all_themes:
            path = os.path.join(self.themes_path, file_name)
            if os.path.exists(path):
                break
        else:
            logger.warning(f"Cannot find theme {file_name!r}.")
            return

        try:
            return self._load(path)
        except (JSONDecodeError, TypeError):
            logger.warning(f"Invalid theme {path!r}.")
            return

    def getThemes(self) -> dict[str, Theme]:
        """Return all valid themes found on disk as a dictionary."""

        themes = []
        for file_name in self.all_themes:

            name, ext = os.path.splitext(file_name)
            if ext != ".json":
                continue

            themes.append(name)

        return Converter.table_from(themes)

    def update_palette(self, palette: QtGui.QPalette, theme: Theme) -> None:
        """Set the Theme for the given QPalette."""

        # Colors
        highlighted_color = theme.primary
        if highlighted_color.valueF() > 0.5:
            highlighted_text_color = theme.mantle
        else:
            highlighted_text_color = theme.text

        h, s, v, a = theme.text.getHsvF()
        bright_text_color = QtGui.QColor.fromHsvF(h, s, 1 - v, a)

        # Normal
        if theme.is_dark_theme():
            palette.setColor(ColorRole.Base, theme.mantle)
            palette.setColor(ColorRole.AlternateBase, theme.base)
        else:
            palette.setColor(ColorRole.Base, theme.crust)
            palette.setColor(ColorRole.AlternateBase, theme.mantle)
        palette.setColor(ColorRole.Window, theme.base)
        palette.setColor(ColorRole.WindowText, theme.text)
        palette.setColor(ColorRole.PlaceholderText, theme.overlay1)
        palette.setColor(ColorRole.Text, theme.text)
        palette.setColor(ColorRole.Button, theme.base)
        palette.setColor(ColorRole.ButtonText, theme.text)
        palette.setColor(ColorRole.BrightText, bright_text_color)
        palette.setColor(ColorRole.ToolTipBase, theme.mantle)
        palette.setColor(ColorRole.ToolTipText, theme.overlay2)

        palette.setColor(ColorRole.Highlight, highlighted_color)
        palette.setColor(ColorRole.HighlightedText, highlighted_text_color)
        palette.setColor(ColorRole.Link, theme.secondary)
        palette.setColor(ColorRole.LinkVisited, theme.secondary)

        palette.setColor(ColorRole.Light, theme.crust)
        palette.setColor(ColorRole.Midlight, theme.mantle)
        palette.setColor(ColorRole.Mid, theme.surface0)
        palette.setColor(ColorRole.Dark, theme.surface1)
        palette.setColor(ColorRole.Shadow, theme.overlay0)

        # Inactive
        palette.setColor(ColorGroup.Inactive, ColorRole.Highlight, theme.surface1)
        palette.setColor(ColorGroup.Inactive, ColorRole.Link, theme.surface1)
        palette.setColor(ColorGroup.Inactive, ColorRole.LinkVisited, theme.surface1)

        # Disabled
        palette.setColor(ColorGroup.Disabled, ColorRole.WindowText, theme.overlay1)
        palette.setColor(ColorGroup.Disabled, ColorRole.Base, theme.base)
        palette.setColor(ColorGroup.Disabled, ColorRole.AlternateBase, theme.base)
        palette.setColor(ColorGroup.Disabled, ColorRole.Text, theme.overlay1)
        palette.setColor(ColorGroup.Disabled, ColorRole.PlaceholderText, theme.overlay1)
        palette.setColor(ColorGroup.Disabled, ColorRole.Button, theme.base)
        palette.setColor(ColorGroup.Disabled, ColorRole.ButtonText, theme.overlay1)
        palette.setColor(ColorGroup.Disabled, ColorRole.BrightText, theme.mantle)

        palette.setColor(ColorGroup.Disabled, ColorRole.Highlight, theme.surface2)
        palette.setColor(ColorGroup.Disabled, ColorRole.HighlightedText, theme.surface0)
        palette.setColor(ColorGroup.Disabled, ColorRole.Link, theme.surface0)
        palette.setColor(ColorGroup.Disabled, ColorRole.LinkVisited, theme.surface0)

    def setTheme(self, theme: Theme | str | None, style: str | None = "fusion") -> None:
        """
        Sets the theme and style for the current QApplication.
        By default, set the Fusion style as it works the best with QPalette ColorRoles.
        """

        # Set style
        if style:
            self.app.setStyle(style)

        # Reset theme
        if not theme:
            self.app.setPalette(QtGui.QPalette())
            return

        # Set theme
        if isinstance(theme, str):
            theme = self.getTheme(theme)
            if not theme:
                return

        palette = QtGui.QPalette()
        self.update_palette(palette, theme)
        self.app.setPalette(palette)
        if application := self.app.instance():
            application.setProperty(PROPERTY_NAME, theme)

    def _load(self, path: str) -> Theme:
        """
        Return the theme from `path`.

        :raises FileNotFoundError: if theme cannot be found.
        :raises TypeError: if theme has unexpected data.
        :raises JSONDecodeError: if theme is invalid json.
        """

        with open(str(path)) as f:
            data = json.load(f)
        colors = {key: QtGui.QColor(value) for key, value in data.items()}
        return Theme(**colors)
