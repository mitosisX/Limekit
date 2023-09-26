from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtGui import QShortcut, QKeySequence


# Responsible for creating those Ctrl+M king of shortcuts
class ShortcutKeys(EnginePart):
    shortcutKeyFunc = None

    def __init__(self, window, shortcut) -> None:
        self.key_sequence = QKeySequence(shortcut)
        self.quitSc = QShortcut(self.key_sequence, window)
        self.quitSc.activated.connect(self.__handleKeys)

    def __handleKeys(self):
        if self.shortcutKeyFunc:
            self.shortcutKeyFunc()

    def setOnKeyPress(self, shortcutKeyFunc):
        self.shortcutKeyFunc = shortcutKeyFunc
