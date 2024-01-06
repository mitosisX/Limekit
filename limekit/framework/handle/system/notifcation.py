from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSystemTrayIcon
from limekit.framework.core.engine.parts import EnginePart
import lupa

"""
It is important to set Tray icon before use. Notice the image not set to None

Remember to call show() for display
"""


class SysNotification(QSystemTrayIcon, EnginePart):
    onShownFunc = None
    onClickedFunc = None

    def __init__(self, image=""):
        super().__init__(QIcon(image), parent=None)
        self.setVisible(True)
        # self.MessageIcon(QIcon(image))
        # self.activated.connect(self.__handleOnShown) # not working - needs research
        self.messageClicked.connect(self.__handleOnClick)

    # def setOnShown(self, onShownFunc):
    #     self.onShownFunc = onShownFunc

    def __handleOnShown(self):
        if self.onShownFunc:
            self.onShownFunc(self)

    def setOnClick(self, onClickedFunc):
        self.onClickedFunc = onClickedFunc

    def __handleOnClick(self):
        if self.onClickedFunc:
            self.onClickedFunc(self)

    @lupa.unpacks_lua_table_method
    def setMessage(self, title="Limekit", message="", icon="", duration=10000):
        icon_map = {
            "noicon": QSystemTrayIcon.MessageIcon.NoIcon,
            "information": QSystemTrayIcon.MessageIcon.Information,
            "warning": QSystemTrayIcon.MessageIcon.Warning,
            "critical": QSystemTrayIcon.MessageIcon.Critical,
        }

        icon_value = icon_map.get(icon.lower(), QSystemTrayIcon.MessageIcon.Information)

        if self.isSystemTrayAvailable():
            self.showMessage(
                title,
                message,
                icon_value,
                duration,
            )
        else:
            print("No System Tray available")

    # Not working at all, best set the visiblity in constructor
    # def show(self):
    #     self.setVisible(True)

    # def hide(self):
    #     self.setVisible(False)
