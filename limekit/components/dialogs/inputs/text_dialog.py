from PySide6.QtWidgets import QInputDialog
from limekit.engine.parts import EnginePart


class TextInputDialog(EnginePart):
    name = "__textInputDialog"

    @classmethod
    def show(cls, parent=None, title="Title", text="Dialog content"):
        text, dialog = QInputDialog.getText(parent, title, text)

        return text if dialog else None

    def isDone(self):
        return self.dialog and self.text != ""

    def getText(self):
        return self.text
