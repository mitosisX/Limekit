from PySide6.QtCore import QResource

from limekit.framework.core.runner.app import App
import os


class MiscellaneousStyle:
    def __init__(self):
        self.app = App.app

        self.dir_path = os.path.abspath(os.path.dirname(__file__))
        self.themes_path = os.path.join(self.dir_path, "themes")

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

    """
    list_themes() returns themes without an .qss extention coz 
    that's too long to remember and type.
    
    Example:
        'dark_teal.xml' -> 'dark_teal'
        - Not much of a big difference, I know, but the latter
          looks much friendlier than former.
    """

    def getThemes(self):
        return [
            theme.rsplit(".qss")[0].lower()
            for theme in os.listdir(self.themes_path)
            if theme.endswith(".qss")
        ]

    def __join_path(self, *paths):
        return os.path.join(paths)
