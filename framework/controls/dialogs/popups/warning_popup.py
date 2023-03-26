from PySide6.QtWidgets import QMessageBox

class WarningPopup:
    # The title can contain HTML elements too
    def __init__(self, parent, title, message):
        self.msg_box = QMessageBox.warning(parent, title, message)