from PySide6.QtWidgets import QInputDialog
from limekit.framework.core.engine.parts import EnginePart


class InputDialog(EnginePart):
    def __init__(self, parent=None, title="Title", text="Dialog content"):
        self.dialog = QInputDialog.getText(parent, title, text)

    def getText(self):
        return str(self.dialog[0])
