import os

from PySide6.QtCore import QResource
from limekit.engine.lifecycle.app import App
from limekit.utils.converters import Converter


class MiscellaneousStyle:
    def __init__(self):
        self.app = App.app

        self.dir_path = os.path.abspath(os.path.dirname(__file__))
        # Assets moved to limekit/assets/themes/misc/, shared with the 2.0
        # engine, so neither engine owns the other's data. Four levels up from
        # limekit/core/theming/themes/misc/ is the limekit package root.
        self.themes_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.dirname(self.dir_path)))),
            "assets", "themes", "misc",
        )

    def setTheme(self, theme):
        theme_name = os.path.join(self.themes_path, f"{theme.lower()}.qss")

        sel_theme = theme.lower()

        if sel_theme == "ue":
            QResource.registerResource(os.path.join(self.themes_path, "icons.rcc"))
        elif sel_theme == "fluent":
            theme_name = os.path.join(
                self.themes_path, "fluent-theme", "LightNoMica.qss"
            )

        with open(theme_name) as theme_read:
            theme_content = theme_read.read()
            self.app.setStyleSheet(theme_content)

    def getThemes(self):
        return Converter.to_lua_table(
            [
                theme.rsplit(".qss")[0].lower()
                for theme in os.listdir(self.themes_path)
                if theme.endswith(".qss")
            ]
        )
