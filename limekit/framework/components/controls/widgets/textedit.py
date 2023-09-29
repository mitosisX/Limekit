from PySide6.QtWidgets import QTextEdit
from limekit.framework.core.engine.parts import EnginePart


# setInputMask("AAAA.AAA.000.000;_"); - limits text to st then ints
class TextField(QTextEdit, EnginePart):
    def __init__(self):
        super().__init__()

    def onTextChange(self, func):
        self.textChanged.connect(lambda: func(self, self.text()))

    def onReturn(self, func):
        self.returnPressed.connect(lambda: func(self))

    def onSelection(self, func):
        self.selectionChanged.connect(lambda: func(self, self.selectedText()))

    def setInputMode(self, input_mode):
        mode = input_mode.lower()

        if mode == "normal":
            self.setEchoMode(QTextEdit.Normal)

        elif mode == "password":
            self.setEchoMode(QTextEdit.Password)

    def setHint(self, hint):
        self.setPlaceholderText(hint)

    def setText(self, text):
        self.setPlainText(text)

    def getText(self):
        return self.toPlainText()
