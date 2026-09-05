"""Keyboard shortcuts -- the Ctrl+M kind.

`QShortcut.activated` is a real signal, so this is an `Event` rather than a
hand-rolled callback slot. The 1.x version stored the handler on a class
attribute (`shortcutKeyFunc = None`), which every instance shared until one
of them assigned over it, and called it unguarded -- an error in a shortcut
handler escaped into the Qt event loop.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut

from limekit.kernel.coerce import Enum
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import Event, Prop, method

# Where a shortcut listens. "window" is Qt's default: anywhere in the window
# the parent belongs to. "widget" means only while the parent, or something
# inside it, has focus -- what a Delete key inside one tab of a window needs,
# or every text field in every other tab loses its Delete.
_SCOPES = {
    "window": Qt.ShortcutContext.WindowShortcut,
    "widget": Qt.ShortcutContext.WidgetWithChildrenShortcut,
    "application": Qt.ShortcutContext.ApplicationShortcut,
}
_scope = Enum(_SCOPES, "shortcut scope")


class KeyboardShortcut(LimeObject, QShortcut):
    __lime__ = "ui.KeyboardShortcut"

    enabled = Prop(bool, qt=("isEnabled", "setEnabled"))
    autoRepeat = Prop(bool, qt=("autoRepeat", "setAutoRepeat"))

    onPress = Event("activated", passes_self=True,
                    doc="Fired when the key sequence is pressed.")

    def __init__(self, parent, sequence):
        if parent is None:
            raise BridgeError(
                "KeyboardShortcut needs a parent widget to bind to; "
                "pass the window it belongs to"
            )
        super().__init__(QKeySequence(str(sequence)), parent)

    @method({"scope": '"window"|"widget"|"application"'}, returns="self",
            doc="Where the shortcut listens: the whole window (default), only "
                "while its parent widget or a child has focus, or everywhere.")
    def setScope(self, scope):
        self.setContext(_scope(scope))
        return self

    def getSequence(self):
        return self.key().toString()

    def setSequence(self, sequence):
        self.setKey(QKeySequence(str(sequence)))
        return self

    # 1.x named this setOnKeyPress; keep it working alongside the generated
    # setOnPress so existing muscle memory still resolves.
    def setOnKeyPress(self, handler):
        return self.setOnPress(handler)
