try:
    import qdarkstyle
    from qdarkstyle.dark.palette import DarkPalette
    from qdarkstyle.light.palette import LightPalette
    _HAS_QDARKSTYLE = True
except ImportError:
    _HAS_QDARKSTYLE = False

from limekit.engine.lifecycle.app import App
from limekit.utils.converters import Converter


class DarkStyle:
    def __init__(self):
        self.app = App.app

    def setTheme(self, theme):
        if not _HAS_QDARKSTYLE:
            from limekit.core.error_handler import warn
            warn("qdarkstyle not installed. Install with: pip install qdarkstyle", "Theme")
            return
        style = qdarkstyle.load_stylesheet(
            palette=DarkPalette if theme == "dark" else LightPalette
        )
        App.app.setStyleSheet(style)

    def getThemes(self):
        if not _HAS_QDARKSTYLE:
            return Converter.to_lua_table([])
        return Converter.to_lua_table(["dark", "light"])
