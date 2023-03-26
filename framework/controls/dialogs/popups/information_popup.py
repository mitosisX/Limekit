from PySide6.QtWidgets import QMessageBox

class InformationPopup:
    # The title can contain HTML elements too
    def __init__(self, parent, title, message):
        self.msg_box = QMessageBox.information(parent, title, message)