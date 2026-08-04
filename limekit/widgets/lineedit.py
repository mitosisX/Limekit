"""Single-line text input.

Unlike TextField (QTextEdit), QLineEdit's own `setText` never guesses HTML,
so `text` can safely be a Prop here -- no `plainText` workaround needed.
"""

from PySide6.QtWidgets import QLineEdit

from limekit.kernel.coerce import CURSORS, Enum
from limekit.kernel.spec import Event, Prop
from limekit.widgets.base import LimeWidget

_cursor = Enum(CURSORS, "cursor")

_ECHO_MODES = {
    "normal": QLineEdit.EchoMode.Normal,
    "password": QLineEdit.EchoMode.Password,
    "hideinput": QLineEdit.EchoMode.NoEcho,
    "passwordonedit": QLineEdit.EchoMode.PasswordEchoOnEdit,
}
_echo_mode = Enum(_ECHO_MODES, "input mode")


class LineEdit(LimeWidget, QLineEdit):
    __lime__ = "ui.LineEdit"

    text = Prop(str, qt=("text", "setText"), coerce=str)
    readOnly = Prop(bool, qt=("isReadOnly", "setReadOnly"))
    maxLength = Prop(int, qt=("maxLength", "setMaxLength"))
    hint = Prop(str, qt=("placeholderText", "setPlaceholderText"), coerce=str,
                doc="placeholder shown while empty")
    inputMode = Prop(object, qt=("echoMode", "setEchoMode"), coerce=_echo_mode,
                      doc="one of: normal, password, hideinput, passwordonedit")

    onTextChange = Event("textChanged", passes_self=True)
    onReturnPress = Event("returnPressed", passes_self=True)
    onTextSelection = Event("selectionChanged", passes_self=True)

    def __init__(self, text=""):
        super().__init__()
        self.setText(text)

    def setAutoComplete(self, completer):
        self.setCompleter(completer)
        return self

    def getSelectedText(self):
        return self.selectedText()

    def checkTextSelected(self):
        return self.hasSelectedText()

    def getStartSelection(self):
        return self.selectionStart()

    def getEndSelection(self):
        return self.selectionEnd()

    def getSelectionLength(self):
        return self.selectionLength()

    def setCursor(self, cursor):
        """Overrides QWidget.setCursor: accepts a Limekit cursor name, not a QCursor."""
        super().setCursor(_cursor(cursor))
        return self

    def selectAll(self):
        """Qt native re-exposed so Lua's `field:selectAll()` colon syntax works."""
        super().selectAll()
        return self

    def undo(self):
        super().undo()
        return self

    def redo(self):
        super().redo()
        return self

    def clear(self):
        super().clear()
        return self
