import qdarktheme
from limekit.framework.handle.scripts.swissknife.converters import Converter


class DarkLight:
    def setTheme(self, theme_type):
        # dark, light or auto
        qdarktheme.setup_theme(theme_type)

    """
    list_themes() returns themes without an .xml extention and 
    that's too long to remenber and type
    
    Example:
        'dark_teal.xml' -> 'dark_teal'
        - Not much of a big difference, I know, but the latter
          looks much friendlier than former.
    """

    def getThemes(self):
        return Converter.table_from(["light", "dark", "auto"])
