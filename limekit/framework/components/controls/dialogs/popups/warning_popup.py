from PySide6.QtWidgets import QMessageBox
from limekit.framework.core.engine.parts import EnginePart


class WarningPopup(EnginePart):
    name = "__wPopup"

    # The title can contain HTML elements too
    def __init__(self, parent, title, message):
        self.msg_box = QMessageBox.warning(parent, title, message)
