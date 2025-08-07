from limekit.core.theming.themes.qtthemes.theme import QtThemes
from limekit.core.theming.themes.material.theme import MaterialStyle
from limekit.core.theming.themes.misc.theme import MiscellaneousStyle
from limekit.core.theming.themes.darklight.theme import DarkLight
from limekit.core.theming.themes.darkstylesheet.theme import DarkStyle

from limekit.engine.parts import EnginePart


class Theme(EnginePart):
    name = "__themer"

    def __init__(self, theme_type):
        self.default_theme = self.__determine_theme(theme_type)

    def __determine_theme(self, theme_type):
        provided_theme = theme_type.lower()

        if provided_theme == "material":
            return MaterialStyle()

        elif provided_theme == "misc":
            return MiscellaneousStyle()

        elif provided_theme == "darklight":
            return DarkLight()

        elif provided_theme == "darkstyle":
            return DarkStyle()

        elif provided_theme == "qtthemes":
            return QtThemes()

    # Depending on the theme selected, apply particular theme name
    def setTheme(self, theme=""):
        self.default_theme.setTheme(theme)

    def getThemes(self):
        return self.default_theme.getThemes()
