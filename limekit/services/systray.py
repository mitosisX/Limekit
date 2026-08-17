"""A system tray icon for Lua: `require("limekit.ui").SysTray`.

Ports `limekit/core/systemtray.py` to the 2.0 pattern. `QSystemTrayIcon` is
a `QObject`, not a `QWidget`, so this is a service-style `LimeObject`
rather than a `LimeWidget` -- there is no `resize`/`sizePolicy` surface to
share with the widget mixin.
"""

from PySide6.QtWidgets import QSystemTrayIcon

from limekit.kernel.coerce import Icon
from limekit.kernel.declarative import LimeObject
from limekit.kernel.spec import Event, Prop


class SysTray(LimeObject, QSystemTrayIcon):
    __lime__ = "ui.SysTray"

    icon = Prop(object, qt=("icon", "setIcon"), coerce=Icon,
                doc="the tray icon's image")
    toolTip = Prop(str, qt=("toolTip", "setToolTip"), coerce=str)
    visible = Prop(bool, qt=("isVisible", "setVisible"))
    menu = Prop(object, qt=("contextMenu", "setContextMenu"),
                doc="the tray icon's right-click context menu")

    onActivated = Event("activated", passes_self=True,
                         params=(("reason", "any"),),
                         doc="Fired when the user clicks or double-clicks the tray icon.")

    def __init__(self, icon=None):
        super().__init__()
        if icon is not None:
            self.setIcon(icon)
        self.setVisible(True)

    def show(self):
        super().show()
        return self

    def hide(self):
        super().hide()
        return self
