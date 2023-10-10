from PySide6.QtGui import QAction, QPixmap
from limekit.framework.core.engine.parts import EnginePart

"""
Regular menu item without an arrow on it's side

To make appear as separator, include empty string or dash '-'
"""


class MenuItem(QAction):
    def __init__(self, title=""):
        super().__init__(text=title)

        if title == "" or title == "-":
            self.setSeparator(True)

    def onClick(self, func):
        self.triggered.connect(lambda: func(self))

    def setImage(self, path):
        pixmap = QPixmap(path)
        self.setIcon(pixmap)

    # namespace: core.controls.dockers.menu.menu
    # Receives object of type Menu
    def addSubmenu(self, menu):
        self.addAction(menu)

    def addSubmenus(self, menus):
        for menu in menus:
            self.addAction(menu)
