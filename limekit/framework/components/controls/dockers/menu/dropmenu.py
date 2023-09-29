from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QPixmap


class DropMenu(QMenu, EnginePart):
    def __init__(self, title=None, parent=None):
        super().__init__(title=title, parent=parent)

    def addDropMenu(self, menu):
        self.addMenu(menu)

    def addMenuItem(self, menu):
        self.addAction(menu)

    def setImage(self, path):
        pixmap = QPixmap(path)
        self.setIcon(pixmap)
