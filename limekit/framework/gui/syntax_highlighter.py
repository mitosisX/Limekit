from PySide6.QtGui import QSyntaxHighlighter
from PySide6.QtWidgets import QTextEdit
from limekit.framework.core.runner.app import App
from limekit.framework.core.engine.parts import EnginePart


# Used in app table
class SyntaxHighlighter(QSyntaxHighlighter, EnginePart):
    onHighlightBlockFunc = None

    def __init__(self, parent: QTextEdit = None):
        super().__init__(parent.document())

    def setOnHighlighBlock(self, onHighlightBlockFunc):
        self.onHighlightBlockFunc = onHighlightBlockFunc

    def highlightBlock(self, text):
        if self.onHighlightBlockFunc:
            self.onHighlightBlockFunc(self, text)

    def setFormat(self, start, length, format):
        super().setFormat(start, length, format)
