from limekit.framework.handle.theming.modern.theme import ModernStyle
from limekit.framework.handle.theming.material.theme import MaterialStyle
from limekit.framework.handle.theming.misc.theme import MiscellaneousStyle

from limekit.framework.core.engine.parts import EnginePart


class Theme(EnginePart):
    def __init__(self, theme_type="material"):
        self.default_theme = self.__determine_theme(theme_type)

    def __determine_theme(self, theme_type):
        provided_theme = theme_type.lower()

        if provided_theme == "material":
            return MaterialStyle()
        elif provided_theme == "modern":
            return ModernStyle()
        elif provided_theme == "misc":
            return MiscellaneousStyle()

    # Depending on the theme selected, apply particular theme name
    def setTheme(self, theme=""):
        self.default_theme.setTheme(theme)

    def getThemes(self):
        return self.default_theme.getThemes()
