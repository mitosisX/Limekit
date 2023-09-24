from PySide6.QtWidgets import QMessageBox
from limekit.framework.core.engine.parts import EnginePart


class CriticalPopup(EnginePart):
    name = "__cPopup"

    # The title can contain HTML elements too
    def __init__(self, parent, title, message):
        self.msg_box = QMessageBox.critical(parent, title, message)

    def getSelectedButton(self):
        if self.msg_box == QMessageBox.Yes:
            return "yes"
        elif self.msg_box == QMessageBox.No:
            return "no"
