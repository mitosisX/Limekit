"""A word-completion popup for Lua: `require("limekit.ui").AutoComplete`.

Ports `limekit/gui/autocomplete.py` to the 2.0 pattern. `QCompleter` is a
`QObject`, not a `QWidget`; attach one to a text field with
`LineEdit:setAutoComplete(completer)` (see `limekit/widgets/lineedit.py`).
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCompleter

from limekit.kernel.bridge.convert import as_sequence
from limekit.kernel.declarative import LimeObject


class AutoComplete(LimeObject, QCompleter):
    __lime__ = "ui.AutoComplete"

    def __init__(self, data=None):
        super().__init__(list(as_sequence(data)) if data is not None else [])
        self.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.setWrapAround(False)

    def setCaseSensitive(self, sensitive):
        """Hand-written rather than a `Prop`: Qt's own getter/setter pair
        here is asymmetric -- `caseSensitivity()` returns a
        `Qt.CaseSensitivity` enum member, not the plain bool Lua callers
        pass to `setCaseSensitivity`. Converting both ways explicitly keeps
        the Lua-facing type a real boolean in both directions."""
        self.setCaseSensitivity(
            Qt.CaseSensitivity.CaseSensitive if sensitive
            else Qt.CaseSensitivity.CaseInsensitive
        )
        return self

    def isCaseSensitive(self):
        return self.caseSensitivity() == Qt.CaseSensitivity.CaseSensitive
