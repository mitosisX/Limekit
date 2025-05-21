from limekit.engine.lifecycle.app import App
from PySide6.QtGui import QTextCharFormat, QFont, QColor
from limekit.engine.parts import EnginePart


# Used in app table
class TextFormat(QTextCharFormat, EnginePart):
    def __init__(self):
        super().__init__()

    def setForegroundColor(self, r, g, b):
        self.setForeground(QColor(r, g, b))

    def setFontWeight(self, style):
        weight_mapping = {
            "thin": QFont.Weight.Thin,
            "extralight": QFont.Weight.ExtraLight,
            "light": QFont.Weight.Light,
            "normal": QFont.Weight.Normal,
            "medium": QFont.Weight.Medium,
            "demibold": QFont.Weight.DemiBold,
            "bold": QFont.Weight.Bold,
            "extrabold": QFont.Weight.ExtraBold,
            "black": QFont.Weight.Black,
        }

        style_lower = style.lower()

        if style_lower in weight_mapping:
            super().setFontWeight(weight_mapping[style_lower])
