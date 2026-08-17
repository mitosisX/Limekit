"""Multi-line text editor.

The 1.x TextField carried ~70 hand-written methods and eight class-level
handler slots. This migration covers the surface the framework's own examples
actually use; the rest lands as P1 needs it, declaratively rather than by
hand.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTextEdit

from limekit.kernel.coerce import ALIGNMENTS, Enum
from limekit.kernel.spec import Event, Prop
from limekit.widgets.base import LimeWidget, _to_int

_alignment = Enum(ALIGNMENTS, "alignment")

_WRAP_MODES = {
    "none": QTextEdit.LineWrapMode.NoWrap,
    "widget": QTextEdit.LineWrapMode.WidgetWidth,
    "fixedpixel": QTextEdit.LineWrapMode.FixedPixelWidth,
    "fixedcolumn": QTextEdit.LineWrapMode.FixedColumnWidth,
}
_wrap_mode = Enum(_WRAP_MODES, "wrap mode")


class TextField(LimeWidget, QTextEdit):
    __lime__ = "ui.TextField"

    # Deliberately `plainText`, not `text`: a `text` Prop would generate a
    # `setText` that silently replaces QTextEdit.setText -- a *different*
    # method, which auto-detects HTML. The kernel's collision guard refuses
    # that, correctly. getText/setText below are hand-written aliases that
    # commit to plain text explicitly.
    plainText = Prop(str, qt=("toPlainText", "setPlainText"), coerce=str,
                     doc="the editor's plain-text content")
    html = Prop(str, qt=("toHtml", "setHtml"), coerce=str)
    readOnly = Prop(bool, qt=("isReadOnly", "setReadOnly"))
    hint = Prop(str, qt=("placeholderText", "setPlaceholderText"), coerce=str,
                doc="placeholder shown while empty")

    onTextChange = Event("textChanged", passes_self=True,
                         doc="Fired whenever the text changes. Unlike LineEdit's, this "
                             "Qt signal carries no text -- read it with getText().")
    onCursorMove = Event("cursorPositionChanged", passes_self=True)

    def __init__(self, text=""):
        super().__init__()
        self.setText(text)

    def getText(self):
        return self.toPlainText()

    def setText(self, text):
        """Always plain text. QTextEdit.setText would guess HTML."""
        self.setPlainText(str(text))
        return self

    def appendText(self, text):
        self.append(str(text))
        return self

    def setWrapMode(self, mode):
        self.setLineWrapMode(_wrap_mode(mode))
        return self

    def setTextAlignment(self, *alignments):
        flags = _alignment(alignments[0])
        for name in alignments[1:]:
            flags |= _alignment(name)
        self.setAlignment(flags)
        return self

    def setTextSize(self, size):
        font = self.font()
        font.setPointSize(_to_int(size, "size"))
        self.setFont(font)
        return self

    def setTextColor(self, colour):
        self.setStyleSheet(f"color: {colour};")
        return self

    def getLineCount(self):
        return self.document().blockCount()

    def scrollToEnd(self):
        bar = self.verticalScrollBar()
        bar.setValue(bar.maximum())
        return self

    def clear(self):
        super().clear()
        return self
