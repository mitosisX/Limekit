import qtmodern.styles
import qtmodern.windows

from framework.kernel.runner.app import App

class ModernStyle:
    def __init__(self):
        self.app = App.app
        
    def setTheme(self, theme='light'):
        theme_functions = {
            'light': qtmodern.styles.light,
            'dark': qtmodern.styles.dark
            }
        
        theme_functions.get(theme, qtmodern.styles.light)(self.app)
        
    def getThemes(self):
        return ["light", "dark"]