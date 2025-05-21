from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QIcon
from limekit.engine.parts import EnginePart
from limekit.utils.converters import Converter


class QuestionPopup(QMessageBox, EnginePart):
    name = "__qPopup"

    result = None

    # The title can contain HTML elements too
    def __init__(self, parent, title, message, buttons=None):
        self.msg_box = self.question(
            parent, title, message, self.__decideButtons(buttons)
        )

    def __decideButtons(self, _buttons):
        buttons = (
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            if not _buttons
            else QMessageBox.StandardButton.NoButton
        )

        button_mapping = {
            "ok": QMessageBox.StandardButton.Ok,
            "open": QMessageBox.StandardButton.Open,
            "save": QMessageBox.StandardButton.Save,
            "cancel": QMessageBox.StandardButton.Cancel,
            "close": QMessageBox.StandardButton.Close,
            "apply": QMessageBox.StandardButton.Apply,
            "restoredefaults": QMessageBox.StandardButton.RestoreDefaults,
            "help": QMessageBox.StandardButton.Help,
            "saveall": QMessageBox.StandardButton.SaveAll,
            "yes": QMessageBox.StandardButton.Yes,
            "reset": QMessageBox.StandardButton.Reset,
            "yestoall": QMessageBox.StandardButton.YesToAll,
            "discard": QMessageBox.StandardButton.Discard,
            "no": QMessageBox.StandardButton.No,
            "notoall": QMessageBox.StandardButton.NoToAll,
            "abort": QMessageBox.StandardButton.Abort,
            "retry": QMessageBox.StandardButton.Retry,
            "ignore": QMessageBox.StandardButton.Ignore,
        }

        try:
            for _button in _buttons.values():
                if button_mapping.get(_button.lower()):
                    print("##### ", _button)
                    buttons |= button_mapping[_button.lower()]

        except AttributeError:
            pass

        return buttons

    def display(self):
        print(self.msg_box)
        if self.msg_box == QMessageBox.StandardButton.Yes:
            return True

        elif self.msg_box == QMessageBox.StandardButton.No:
            return False
