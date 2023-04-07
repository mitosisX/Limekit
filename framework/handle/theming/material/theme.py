from qt_material import apply_stylesheet
from qt_material import list_themes

from framework.kernel.runner.app import App

class MaterialStyle:
    def __init__(self):
        self.app = App.app
        
    def setTheme(self, theme='light_blue'):
        apply_stylesheet(self.app, f'{theme}.xml')
    
    """
    list_themes() returns themes with a .xml extention and 
    that's too long to type.
    
    Example:
        'dark_teal.xml' -> 'dark_teal'
        - Not much of a big difference, I know, But that doesn't
          look much friendlier than this.
    """
    def getThemes(self):
        return [theme.rsplit('.')[0] for theme in list_themes()]