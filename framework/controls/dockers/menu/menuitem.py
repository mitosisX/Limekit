from PySide6.QtGui import QAction
from PySide6.QtGui import QPixmap

class MenuItem(QAction):
    def __init__(self, title = None):
        super().__init__(title)

    def onClick(self, func):
        self.triggered.connect(lambda: func(self))

    def setImage(self, path):
        pixmap = QPixmap(path)
        self.setIcon(pixmap)
        
    # namespace: core.controls.dockers.menu.menu
    # Receives object of type Menu
    def addMenuItem(self, menu):
        self.setIcon(menu)