import qdarkstyle
from qdarkstyle.dark.palette import DarkPalette
from qdarkstyle.light.palette import LightPalette
from limekit.engine.lifecycle.app import App
from limekit.utils.converters import Converter


class DarkStyle:
    def __init__(self):
        self.app = App.app

    def setTheme(self, theme):
        style = qdarkstyle.load_stylesheet(
            palette=DarkPalette if theme == "dark" else LightPalette
        )
        App.app.setStyleSheet(style)

    def getThemes(self):
        return Converter.to_lua_table(["dark", "light"])
