from PySide6.QtWidgets import QLineEdit
from limekit.framework.core.engine.parts import EnginePart


# setInputMask("AAAA.AAA.000.000;_"); - limits text to st then ints
class LineEdit(QLineEdit, EnginePart):
    def __init__(self, text=""):
        super().__init__(text)

    def onTextChange(self, func):
        self.textChanged[str].connect(lambda: func(self, self.text()))

    def onReturn(self, func):
        self.returnPressed.connect(lambda: func(self))

    def onSelection(self, func):
        self.selectionChanged.connect(lambda: func(self, self.selectedText()))

    def setInputMode(self, input_mode):
        mode = input_mode.lower()

        if mode == "normal":
            self.setEchoMode(QLineEdit.Normal)

        elif mode == "password":
            self.setEchoMode(QLineEdit.Password)

    def setText(self, text):
        super().setText(text)

    def setHint(self, hint):
        self.setPlaceholderText(hint)

    def getText(self):
        return self.text()
