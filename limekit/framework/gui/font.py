from limekit.framework.core.runner.app import App
from PySide6.QtGui import QFont, QFontDatabase
from limekit.framework.core.engine.parts import EnginePart


# Used in app table
class Font(EnginePart):
    name = "__font"

    @staticmethod
    def set_font(font, size):
        font_id = QFontDatabase.addApplicationFont(font)

        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            custom_font = QFont(font_family, size)
            App.app.setFont(custom_font)

    # app.setFontFile(file)
    @staticmethod
    def from_file(file):
        font = QFont(file)
        App.app.setFont(font)

    @classmethod
    def set_font_size(cls, size):
        font = QFont()
        font.setPointSize(size)
        App.app.setFont(font)
