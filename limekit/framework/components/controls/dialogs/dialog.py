from PySide6.QtWidgets import QDialog, QDialogButtonBox
from PySide6.QtGui import QIcon
from limekit.framework.core.engine.parts import EnginePart

"""
This is a Dumb Dialog. Oftenly used for "Ok", "Cancel" operations
"""


class DialogBox(QDialog, EnginePart):
    name = "Modal"

    def __init__(self, parent, title):
        super().__init__(parent)

        self.setWindowTitle(title)

        self.buttons = QDialogButtonBox.StandardButton.Ok

        # self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setDefault(True)

    def setLayout(self, layout):
        super().setLayout(layout)

    def setIcon(self, icon):
        self.setWindowIcon(QIcon(icon))

    def getButtons(self, buttons):
        return QDialogButtonBox(self.__decideButtons(buttons))

    def __decideButtons(self, _buttons):
        if _buttons:
            for _button in _buttons.values():
                button = str(_button).lower()

                if button == "ok":
                    self.buttons |= QDialogButtonBox.StandardButton.Ok

                elif button == "open":
                    self.buttons |= QDialogButtonBox.StandardButton.Open

                elif button == "save":
                    self.buttons |= QDialogButtonBox.StandardButton.Save

                elif button == "cancel":
                    self.buttons |= QDialogButtonBox.StandardButton.Cancel

                elif button == "close":
                    self.buttons |= QDialogButtonBox.StandardButton.Close

                elif button == "apply":
                    self.buttons |= QDialogButtonBox.StandardButton.Apply

                elif button == "restoredefaults":
                    self.buttons |= QDialogButtonBox.StandardButton.RestoreDefaults

                elif button == "help":
                    self.buttons |= QDialogButtonBox.StandardButton.Help

                elif button == "saveall":
                    self.buttons |= QDialogButtonBox.StandardButton.SaveAll

                elif button == "yes":
                    self.buttons |= QDialogButtonBox.StandardButton.Yes

                elif button == "saveall":
                    self.buttons |= QDialogButtonBox.StandardButton.Close

                elif button == "reset":
                    self.buttons |= QDialogButtonBox.StandardButton.Reset

                elif button == "yestoall":
                    self.buttons |= QDialogButtonBox.StandardButton.YesToAll

                elif button == "discard":
                    self.buttons |= QDialogButtonBox.StandardButton.Discard

                elif button == "notoall":
                    self.buttons |= QDialogButtonBox.StandardButton.NoToAll

                elif button == "abort":
                    self.buttons |= QDialogButtonBox.StandardButton.Abort

                elif button == "retry":
                    self.buttons |= QDialogButtonBox.StandardButton.Retry

                elif button == "ignore":
                    self.buttons |= QDialogButtonBox.StandardButton.Ignore

            return self.buttons

        else:
            self.buttons |= QDialogButtonBox.StandardButton.Ok

            return self.buttons

    def show(self):
        self.exec()
