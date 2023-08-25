from PySide6.QtWidgets import QMessageBox
from limekit.framework.core.engine.parts import EnginePart


class QuestionPopup(EnginePart):
    name = "__qPopup"

    # The title can contain HTML elements too
    def __init__(self, parent, title, message, buttons):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        # Map the button text to the standard button
        button_map = {
            "yes": QMessageBox.Yes,
            "no": QMessageBox.No,
            "cancel": QMessageBox.Cancel,
            "ok": QMessageBox.Ok,
            "abort": QMessageBox.Abort,
            "retry": QMessageBox.Retry,
            "ignore": QMessageBox.Ignore,
            "save": QMessageBox.Save,
            "discard": QMessageBox.Discard,
            "apply": QMessageBox.Apply,
            "reset": QMessageBox.Reset,
            "restoredefaults": QMessageBox.RestoreDefaults,
        }

        # Add each button to the message box
        for button_text in buttons:
            button = button_map.get(button_text.lower())
            if button is not None:
                msg_box.addButton(button_text.lower(), button)

        # Display the message box and return the clicked button
        return msg_box.exec_()
