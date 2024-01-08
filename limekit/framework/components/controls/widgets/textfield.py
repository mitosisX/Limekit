from PySide6.QtWidgets import QTextEdit
from limekit.framework.core.engine.parts import EnginePart


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

    def setOnSelection(self, onTextSelectionChangedFunc):
        self.onTextSelectionChangedFunc = onTextSelectionChangedFunc

    def __handleTextSelection(self):
        if self.onTextSelectionChangedFunc:
            self.onTextSelectionChangedFunc(self, self.selectedText())

    # --------------------------------- Events

    def setSize(self, width, height):
        self.resize(width, height)

    def setMinHeight(self, height):
        self.setMinimumHeight(height)

    def setMaxHeight(self, height):
        self.setMaximumHeight(height)

    def setMinWidth(self, width):
        self.setMinimumWidth(width)

    def setMaxWidth(self, width):
        self.setMaximumWidth(width)

    def setReadOnly(self, readonly):
        super().setReadOnly(readonly)

    def setHint(self, hint):
        self.setPlaceholderText(hint)

    def cut(self):
        super().cut()

    def copy(self):
        super().copy()

    def appendText(self, text):
        self.append(text)

    def setText(self, text):
        self.setPlainText(text)

    def getText(self):
        return self.toPlainText()
