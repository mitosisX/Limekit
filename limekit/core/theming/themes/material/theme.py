try:
    from qt_material import apply_stylesheet, list_themes
    _HAS_QT_MATERIAL = True
except ImportError:
    _HAS_QT_MATERIAL = False

from limekit.engine.lifecycle.app import App
from limekit.utils.converters import Converter


class MaterialStyle:
    def __init__(self):
        self.app = App.app

    def setTheme(self, theme="light_blue"):
        if not _HAS_QT_MATERIAL:
            from limekit.core.error_handler import warn
            warn("qt_material not installed. Install with: pip install qt-material", "Theme")
            return
        apply_stylesheet(self.app, f"{theme}.xml")

    """
    list_themes() returns themes without an .xml extention and 
    that's too long to remenber and type
    
    Example:
        'dark_teal.xml' -> 'dark_teal'
        - Not much of a big difference, I know, but the latter
          looks much friendlier than former.
    """

    def getThemes(self):
        if not _HAS_QT_MATERIAL:
            return Converter.to_lua_table([])
        return Converter.to_lua_table([theme.rsplit(".")[0] for theme in list_themes()])
