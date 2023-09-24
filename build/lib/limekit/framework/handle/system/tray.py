from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QSystemTrayIcon
from limekit.framework.core.engine.parts import EnginePart


class Tray(EnginePart, QSystemTrayIcon):
    name = "SysTray"

    def __init__(self):
        super().__init__()

    def setImage(self, path):
        pixmap = QPixmap(path)
        self.setIcon(pixmap)

    def setMenu(self, menu):
        self.setContextMenu(menu)

    def setVisibility(self, bool):
        self.setVisible(bool)

    def gg(self):
        self.showMessage("Test", "Message", QSystemTrayIcon.Critical, 2000)
