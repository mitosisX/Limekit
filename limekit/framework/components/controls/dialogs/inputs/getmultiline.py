from PySide6.QtWidgets import QInputDialog
from limekit.framework.core.engine.parts import EnginePart


class MultilineInputDialog(EnginePart):
    name = "__multilineInputDialog"

    @classmethod
    def show(cls, parent, title, label, content):
        # content is set to blank in lua "app" table
        text, dialog = QInputDialog.getMultiLineText(parent, title, label, content)
        return text if dialog else None
