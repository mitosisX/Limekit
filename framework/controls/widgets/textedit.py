from PySide6.QtWidgets import QLineEdit


# setInputMask("AAAA.AAA.000.000;_"); - limits text to st then ints
class TextEdit(QLineEdit):

    def __init__(self):
        super().__init__()

    def onTextChange(self, func):
        self.textChanged[str].connect(lambda: func(self, self.text()))

    def onReturn(self, func):
        self.returnPressed.connect(lambda: func(self))

    def onSelection(self, func):
        self.selectionChanged.connect(lambda: func(self, self.selectedText()))

    def setInputMode(self, input_mode):
        mode = input_mode.lower()

        if mode == 'normal':
            self.setEchoMode(QLineEdit.Normal)

        elif mode == 'password':
            self.setEchoMode(QLineEdit.Password)
            
    def setReadonly(self, bool = True):
        self.setReadOnly(bool)
            
    def getText(self):
        return self.text()