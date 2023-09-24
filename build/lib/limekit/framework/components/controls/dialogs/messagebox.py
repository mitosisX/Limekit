from PySide6.QtWidgets import QMessageBox
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.handle.scripts.swissknife.converters import Converter

# QMessageBox.NoIcon
# QMessageBox.Question
# QMessageBox.Information
# QMessageBox.Warning
# QMessageBox.Critical

# QMessageBox.Ok
# QMessageBox.Open
# QMessageBox.Save
# QMessageBox.Cancel
# QMessageBox.Close
# QMessageBox.Discard
# QMessageBox.Apply
# QMessageBox.Reset
# QMessageBox.RestoreDefaults
# QMessageBox.Help
# QMessageBox.SaveAll
# QMessageBox.Yes
# QMessageBox.YesToAll
# QMessageBox.No
# QMessageBox.NoToAll
# QMessageBox.Abort
# QMessageBox.Retry
# QMessageBox.Ignore
# QMessageBox.NoButton


class MessageBox(EnginePart):
    name = "__alert"

    result = None

    def __init__(self, parent, title, text, icon, buttons):
        buttons = Converter.list_(buttons)

        self.dialog = QMessageBox(parent)
        self.dialog.setWindowTitle(title)
        self.dialog.setText(text)
        # self.dialog.setStandardButtons(QMessageBox.Ok)
        self.dialog.setIcon(self.__decideIcon(icon))
        self.dialog.setStandardButtons(self.__decideButtons(buttons))
        self.dialog.exec()

    def getText(self):
        return str(self.dialog[0])

    def show(self):
        self.result = self.dialog.exec()

    # This resolves info type and returns right QMessage property
    def __decideIcon(self, _icon):
        icon = str(_icon).lower()

        if icon == "question":
            return QMessageBox.Question

        elif icon == "information":
            return QMessageBox.Information

        elif icon == "warning":
            return QMessageBox.Warning

        elif icon == "critical":
            return QMessageBox.Critical

        else:
            return QMessageBox.NoIcon

    # QMessageBox.Ok
    # QMessageBox.Open
    # QMessageBox.Save
    # QMessageBox.Cancel
    # QMessageBox.Close
    # QMessageBox.Discard
    # QMessageBox.Apply
    # QMessageBox.Reset
    # QMessageBox.RestoreDefaults
    # QMessageBox.Help
    # QMessageBox.SaveAll
    # QMessageBox.Yes
    # QMessageBox.YesToAll
    # QMessageBox.No
    # QMessageBox.NoToAll
    # QMessageBox.Abort
    # QMessageBox.Retry
    # QMessageBox.Ignore
    # QMessageBox.NoButton

    def __decideButtons(self, _buttons):
        buttons = QMessageBox.NoButton

        if _buttons:
            for _button in _buttons:
                button = str(_button).lower()

                if button == "ok":
                    buttons |= QMessageBox.Ok

                elif button == "open":
                    buttons |= QMessageBox.Open

                elif button == "save":
                    buttons |= QMessageBox.Save

                elif button == "cancel":
                    buttons |= QMessageBox.Cancel

                elif button == "close":
                    buttons |= QMessageBox.Close

                elif button == "apply":
                    buttons |= QMessageBox.Appy

                elif button == "restoredefaults":
                    buttons |= QMessageBox.RestoreDefaults

                elif button == "help":
                    buttons |= QMessageBox.Help

                elif button == "saveall":
                    buttons |= QMessageBox.SaveAll

                elif button == "yes":
                    buttons |= QMessageBox.Yes

                elif button == "saveall":
                    buttons |= QMessageBox.Close

                elif button == "yes":
                    buttons |= QMessageBox.Discard

                elif button == "yestoall":
                    buttons |= QMessageBox.YesToAll

                elif button == "no":
                    buttons |= QMessageBox.Discard

                elif button == "notoall":
                    buttons |= QMessageBox.NoToAll

                elif button == "abort":
                    buttons |= QMessageBox.Abort

                elif button == "retry":
                    buttons |= QMessageBox.Retry

                elif button == "ignore":
                    buttons |= QMessageBox.Ignore

            return buttons

        else:
            buttons |= QMessageBox.Ok

            return buttons
