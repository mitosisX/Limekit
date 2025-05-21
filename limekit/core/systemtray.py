from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSystemTrayIcon
from limekit.engine.parts import EnginePart


class Tray(QSystemTrayIcon, EnginePart):
    name = "SysTray"

    def __init__(self, icon):
        super().__init__()
        if icon:
            self.setIcon(icon)

        self.setVisibility(True)

    def setIcon(self, path):
        super().setIcon(QIcon(path))

    def setToolTip(self, tooltip):
        super().setToolTip(tooltip)

    def setMenu(self, menu):
        self.setContextMenu(menu)

    def setVisibility(self, bool):
        self.setVisible(bool)
