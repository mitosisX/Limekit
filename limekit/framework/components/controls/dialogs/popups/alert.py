from PySide6.QtWidgets import QMessageBox
from limekit.framework.core.engine.parts import EnginePart


class Alert(EnginePart):
    @staticmethod
    def show(parent, title, text):
        dialog = QMessageBox(parent)
        dialog.setWindowTitle(title)
        dialog.setText(text)

        result = dialog.exec()

        if result == QMessageBox.StandardButton.Ok:
            print("OK")
            # return True
        else:
            print("Cancel")
            # return False
