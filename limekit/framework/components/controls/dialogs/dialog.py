from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QDialogButtonBox
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.core.engine.destroyer import destroy_engine

"""
This is a Dumb Dialog. Oftenly used for "Ok", "Cancel" operations
"""


class Dialog(QDialog, EnginePart):
    name = "Modal"
    onShownEvent = None
    onResizeEvent = None
    onCloseEvent = None
    onResizeEvent = None

    def __init__(self, parent, title="Modal - Limkit"):
        super().__init__(parent)

        self.setWindowTitle(title)

        self.buttons = QDialogButtonBox.StandardButton.Ok
        self.dialog_buttons = QDialogButtonBox(self.buttons)

        # self.dialog_buttons.clicked.connect(self.accept)
        # self.dialog_buttons.rejected.connect(self.reject)

        # self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setDefault(True)

    # Events ----------------------
    def setOnShown(self, func):
        self.onShownEvent = func

    def showEvent(self, event):
        super().showEvent(event)
        if self.onShownEvent:
            try:
                self.onShownEvent(self)
            except Exception as ex:
                print(ex)
                destroy_engine()

    def setOnClose(self, func):
        self.onCloseEvent = func

    # event has: ignore and accept
    def closeEvent(self, event):
        if self.onCloseEvent:
            try:
                self.onCloseEvent(self, event)
            except Exception as ex:
                print(ex)
                destroy_engine()

    def setOnResize(self, func):
        self.onResizeEvent = func

    def resizeEvent(self, event):
        if self.onResizeEvent:
            try:
                self.onResizeEvent(self)
            except Exception as ex:
                print(ex)
                destroy_engine()

    # ---------------------- Events

    def setSize(self, width, height):
        self.resize(width, height)

    def setMinSize(self, width, height):
        self.setMinimumSize(width, height)

    def setMinHeight(self, height):
        self.setMinimumHeight(height)

    def setMinWidth(self, width):
        self.setMinimumWidth(width)

    def setMaxHeight(self, height):
        self.setMaximumHeight(height)

    def setMaxWidth(self, width):
        self.setMaximumWidth(width)

    def setMaxSize(self, width, height):
        self.setMaximumSize(width, height)

    def minimize(self):
        self.showMinimized()

    def setLocation(self, x, y):
        self.move(x, y)

    def setLayout(self, layout):
        super().setLayout(layout)

    def dismiss(self):
        self.close()

    def setIcon(self, icon):
        self.setWindowIcon(QIcon(icon))

    def setTitle(self, title):
        self.setWindowTitle(title)

    def getButtons(self, buttons):
        self.dialog_buttons = QDialogButtonBox(self.__decideButtons(buttons))
        return self.dialog_buttons

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
        return self.exec()
