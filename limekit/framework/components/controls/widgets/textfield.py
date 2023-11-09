from PySide6.QtWidgets import QTextEdit
from limekit.framework.core.engine.parts import EnginePart


# setInputMask("AAAA.AAA.000.000;_"); - limits text to st then ints
class TextField(QTextEdit, EnginePart):
    onTextChangedFunc = None
    onTextSelectionChangedFunc = None

    def __init__(self, text=""):
        super().__init__(text)

        self.textChanged.connect(self.__handleTextChange)
        self.selectionChanged.connect(self.__handleTextSelection)

    # Events ---------------------------------
    def setOnTextChange(self, onTextChangedFunc):
        self.onTextChangedFunc = onTextChangedFunc

    def __handleTextChange(self):
        if self.onTextChangedFunc:
            self.onTextChangedFunc(self, self.getText())

    def setOnReturnPress(self, onReturnPressedFunc):
        self.onReturnPressedFunc = onReturnPressedFunc

    def setOnSelection(self, onTextSelectionChangedFunc):
        self.onTextSelectionChangedFunc = onTextSelectionChangedFunc

    def __handleTextSelection(self):
        if self.onTextSelectionChangedFunc:
            self.onTextSelectionChangedFunc(self, self.selectedText())

    # --------------------------------- Events

    def setAutoComplete(self, autocomplete):
        self.setCompleter(autocomplete)

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
