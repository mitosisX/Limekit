from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QIcon
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.handle.scripts.swissknife.converters import Converter


class QuestionPopup(QMessageBox, EnginePart):
    name = "__qPopup"

    result = None

    # The title can contain HTML elements too
    def __init__(self, parent, title, message):
        self.msg_box = self.question(parent, title, message)
        # self.msg_box.setWindowTitle(title)
        # self.msg_box.setText(message)

        # Map the button text to the standard button
        # self.button_map = {
        #     "yes": QMessageBox.Yes,
        #     "no": QMessageBox.No,
        #     "cancel": QMessageBox.Cancel,
        #     "ok": QMessageBox.Ok,
        #     "abort": QMessageBox.Abort,
        #     "retry": QMessageBox.Retry,
        #     "ignore": QMessageBox.Ignore,
        #     "save": QMessageBox.Save,
        #     "discard": QMessageBox.Discard,
        #     "apply": QMessageBox.Apply,
        #     "reset": QMessageBox.Reset,
        #     "restoredefaults": QMessageBox.RestoreDefaults,
        # }

        # # Add each button to the message box
        # for button_text in Converter.list_(buttons):
        #     button_text_ = button_text.lower().strip()

        #     button = button_map.get(button_text_)

        #     if button is not None:
        #         self.msg_box.addButton(button)

        # Display the message box and return the clicked button
        # self.result = self.msg_box.sho()

    def display(self):
        if self.msg_box == QMessageBox.Yes:
            return True
        elif self.msg_box == QMessageBox.No:
            return False
