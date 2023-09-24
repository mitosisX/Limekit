from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QSystemTrayIcon
from limekit.framework.core.engine.parts import EnginePart

"""
It is important to set Tray icon before use. Notice the image not set to None

Remember to call show() for display
"""


class Notification(EnginePart, QSystemTrayIcon):
    def __init__(self, image=""):
        super().__init__(QIcon(image))
        # super().__init__(QIcon(image))
        self.setVisible(True)

    def onShown(self, func):
        self.clicked.activated(lambda: func(self))

    def onClick(self, func):
        self.clicked.messageClicked(lambda: func(self))

    def setMessage(self, title, message, icon, duration):
        icon_map = {
            "noicon": QSystemTrayIcon.NoIcon,
            "information": QSystemTrayIcon.Information,
            "warning": QSystemTrayIcon.Warning,
            "critical": QSystemTrayIcon.Critical,
        }

        icon_value = icon_map.get(icon.lower(), QSystemTrayIcon.Information)

        self.showMessage(
            title,
            message,
            icon_value,
            duration,
        )
