try:
    import qdarktheme
    _HAS_QDARKTHEME = True
except ImportError:
    _HAS_QDARKTHEME = False

from PySide6.QtWidgets import QApplication
from limekit.utils.converters import Converter


class DarkLight:
    def setTheme(self, theme_type):
        # dark, light or auto
        if not _HAS_QDARKTHEME:
            from limekit.core.error_handler import warn
            warn("qdarktheme not installed. Install with: pip install pyqtdarktheme", "Theme")
            return

        app = QApplication.instance()
        if app:
            stylesheet = qdarktheme.load_stylesheet(theme_type)
            app.setStyleSheet(stylesheet)

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
