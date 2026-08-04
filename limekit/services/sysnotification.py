"""A desktop balloon notification for Lua: `require("limekit.ui").SysNotification`.

Ports `limekit/core/system_notifcation.py` (the 1.x filename really is
misspelled -- "notifcation") to the 2.0 pattern, correcting the spelling in
the new module name.

Qt only exposes balloon notifications through `QSystemTrayIcon.showMessage`,
so -- exactly as in 1.x -- this wraps a (normally invisible-to-the-user,
just present-for-the-API) tray icon rather than anything notification-shaped
in Qt itself.

1.x defect not reproduced: `setMessage` checked `isSystemTrayAvailable()`
and silently `print()`-ed "No System Tray available" instead of showing the
message when it returned False. A headless CI box (or any Linux session
without a tray daemon running) would have every single notification calmly
swallowed with nothing but a console print raised nowhere Lua could see it.
`showMessage` here always calls through to Qt's `showMessage`; if the
platform genuinely cannot show it, that is Qt's call to make, not ours to
hide.
"""

from PySide6.QtWidgets import QSystemTrayIcon

from limekit.kernel.bridge.guard import guard
from limekit.kernel.coerce import Enum, Icon
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import Event, Prop

_MESSAGE_ICONS = {
    "none": QSystemTrayIcon.MessageIcon.NoIcon,
    "information": QSystemTrayIcon.MessageIcon.Information,
    "warning": QSystemTrayIcon.MessageIcon.Warning,
    "critical": QSystemTrayIcon.MessageIcon.Critical,
}
_message_icon = Enum(_MESSAGE_ICONS, "notification icon")


def _to_int(value, label):
    """Duplicated from widgets/base.py: services/ must not import widgets/."""
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise BridgeError(f"expected a number for {label}, got {value!r}") from exc


class SysNotification(LimeObject, QSystemTrayIcon):
    __lime__ = "ui.SysNotification"

    icon = Prop(object, qt=("icon", "setIcon"), coerce=Icon,
                doc="the notification's icon")

    onClick = Event("messageClicked", passes_self=True,
                     doc="Fired when the user clicks the notification balloon.")

    def __init__(self, icon=None):
        super().__init__()
        if icon is not None:
            self.setIcon(icon)
        self.setVisible(True)

    def showMessage(self, title, message, icon="information", duration=3000):
        """Pop a balloon notification.

        `icon` is one of "none", "information", "warning", "critical";
        `duration` is in milliseconds, matching Qt's own unit.
        """
        kind = _message_icon(icon)
        super().showMessage(str(title), str(message), kind,
                             _to_int(duration, "duration"))
        return self
