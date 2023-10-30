from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QSystemTrayIcon
from limekit.framework.core.engine.parts import EnginePart


class Tray(QSystemTrayIcon, EnginePart):
    name = "SysTray"

    def __init__(self, icon):
        super().__init__()
        if icon:
            self.setImage(icon)

        self.setVisibility(True)

    def setImage(self, path):
        pixmap = QPixmap(path)
        self.setIcon(QIcon(path))

    def setMenu(self, menu):
        self.setContextMenu(menu)

    def setVisibility(self, bool):
        self.setVisible(bool)
