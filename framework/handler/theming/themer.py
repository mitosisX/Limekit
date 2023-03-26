from .material.theme import MaterialStyle
from .modern.theme import ModernStyle

class Theme:
    def __init__(self, theme_type):
        self.default_theme = self.__determine_theme(theme_type)

    def __determine_theme(self, theme_type):
        if theme_type.lower() == 'material':
            return MaterialStyle()
        elif theme_type.lower() == 'modern':
            return ModernStyle()
        
    # Depending on the theme selected, apply particular theme name
    def setTheme(self, theme = ""):
        self.default_theme.setTheme(theme)
    
    def getThemes(self):
        return self.default_theme.getThemes()