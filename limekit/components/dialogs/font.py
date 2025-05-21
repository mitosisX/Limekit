from limekit.engine.parts import EnginePart
from PySide6.QtWidgets import QFontDialog


class FontDialog(EnginePart):
    name = "__fontDialog"

    def display(self):
        font, ok = QFontDialog.getFont()
        return ok if ok else None
