from PySide6.QtWidgets import QMessageBox

class CriticalPopup:
    # The title can contain HTML elements too
    def __init__(self, parent, title, message):
        self.msg_box = QMessageBox.critical(parent, title, message)