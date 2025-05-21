import lupa
from limekit.engine.parts import EnginePart
from PySide6.QtWidgets import QCompleter
from PySide6.QtCore import Qt


class AutoComplete(QCompleter, EnginePart):
    def __init__(self, data):
        super().__init__(data.values() if lupa.lua_type(data) == "table" else data)

        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.setWrapAround(False)
