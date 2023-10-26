from PySide6.QtWidgets import QErrorMessage
from limekit.framework.core.engine.parts import EnginePart


class TextInputDialog(EnginePart):
    name = "__errorDialog"

    _instance = None

    # At first, the "do not show this message" checkbutton wasn't working
    # and I resorted to make the class singleton (design pattern)
    def __new__(cls, parent, title, message):
        if cls._instance is None:
            # If an instance does not exist, create one
            cls._instance = super(TextInputDialog, cls).__new__(cls)
            cls._instance.init_dialog(parent, title, message)
        return cls._instance

    def init_dialog(self, parent, title, message):
        self.dialog = QErrorMessage(parent=parent)
        self.dialog.setWindowTitle(title)
        self.dialog.showMessage(message)
