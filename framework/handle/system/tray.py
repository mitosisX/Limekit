from PySide6.QtWidgets import QSystemTrayIcon
from PySide6.QtGui import QPixmap

class Tray(QSystemTrayIcon):
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