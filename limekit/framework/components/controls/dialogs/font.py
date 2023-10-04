from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtWidgets import QFontDialog


class FontDialog(QFontDialog, EnginePart):
    name = "__fontDialog"

    def __init__(self, parent):
        super().__init__(parent)
        self.name_ = None

    def setInitDir(self, dir):
        self.setDirectory(dir)

    def display(self):
        (self.name_, ok) = self.getFont()

    def get(self):
        return self.name_ if self.name_ else None
