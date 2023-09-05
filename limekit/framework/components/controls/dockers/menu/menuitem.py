import PySide6.QtCore
from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QPixmap
from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtCore import QObject, QEvent


class MenuItem(QMenu, EnginePart):
    def __init__(self, title):
        super().__init__(title)

    def onClick(self, func):
        self.triggered.connect(lambda: func(self))

    def setImage(self, path):
        pixmap = QPixmap(path)
        self.setIcon(pixmap)

    def addSubmenu(self, menuitem):
        self.addAction(menuitem)

    # namespace: core.controls.dockers.menu.menuitems
    # Receives object of type Menu, basically another QAction
    def addSubmenus(self, *menuitems):
        for menuitem in menuitems:
            self.addAction(menuitem)
