from PySide6.QtWidgets import QInputDialog
from limekit.framework.core.engine.parts import EnginePart


class InputDialog(EnginePart):
    name = "__inputDialog"

    def __init__(self, parent=None, title="Title", text="Dialog content"):
        self.text, self.dialog = QInputDialog.getText(parent, title, text)

    def isDone(self):
        return self.dialog and self.text != ""

    def getText(self):
        return self.text
