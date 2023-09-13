from limekit.framework.core.runner.app import App
from PySide6.QtGui import QFont, QFontDatabase
from limekit.framework.core.engine.app_engine import EnginePart


class Font(EnginePart):
    name = "__font"

    @classmethod
    def set_font(cls, font, size):
        font_id = QFontDatabase.addApplicationFont(font)

        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            custom_font = QFont(font_family, size)
            App.app.setFont(custom_font)
