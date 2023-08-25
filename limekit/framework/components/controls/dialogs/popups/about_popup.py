from PySide6.QtWidgets import QMessageBox
from limekit.framework.core.engine.parts import EnginePart


class AboutPopup(EnginePart):
    name = "__aPopup"

    # The title can contain HTML elements too
    def __init__(self, parent=None, title="", message=""):
        self.msg_box = QMessageBox.about(parent, title, message)
