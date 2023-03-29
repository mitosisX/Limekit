from .material.theme import MaterialStyle
from .modern.theme import ModernStyle
from .misc.theme import MiscellaneousStyle

class Theme:
    def __init__(self, theme_type):
        self.default_theme = self.__determine_theme(theme_type)

    def __determine_theme(self, theme_type):
        provided_theme = theme_type.lower()
        
        if provided_theme == 'material':
            return MaterialStyle()
        elif provided_theme == 'modern':
            return ModernStyle()
        elif provided_theme == 'misc':
            return MiscellaneousStyle()
        
    # Depending on the theme selected, apply particular theme name
    def setTheme(self, theme = ""):
        self.default_theme.setTheme(theme)
    
    def getThemes(self):
        return self.default_theme.getThemes()