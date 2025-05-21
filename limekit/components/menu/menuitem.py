from PySide6.QtGui import QAction
from PySide6.QtGui import QIcon, QFont
from limekit.engine.parts import EnginePart


class MenuItem(QAction, EnginePart):
    onClickFunction = None

    def __init__(self, title=None, parent=None):
        super().__init__(text=title if title != "-" else "", parent=parent)

        if title == "-":
            self.setSeparator(True)

        font = QFont()
        font.setPointSize(8)
        self.setFont(font)

        self.triggered.connect(self.__handleOnClick)

    def setText(self, text):
        super().setText(text)

    def getText(self):
        return self.text()

    def __handleOnClick(self):
        if self.onClickFunction:
            try:
                self.onClickFunction(self)
            except Exception as ex:
                print(ex)

    def setOnClick(self, onClickFunction):
        self.onClickFunction = onClickFunction

    def setIcon(self, path):
        super().setIcon(QIcon(path))

    def addMenuItem(self, menuitem):
        self.addAction(menuitem)

    # namespace: core.controls.dockers.menu.menuitems
    # Receives object of type Menu, basically another QAction
    def addSubmenus(self, *menuitems):
        for menuitem in menuitems:
            self.addAction(menuitem)

    def setShortcut(self, shortcut):
        super().setShortcut(shortcut)
