import sys
import uuid

from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QFrame
from qfluentwidgets import FluentWindow, isDarkTheme


def isWin11():
    return sys.platform == "win32" and sys.getwindowsversion().build >= 22000


class Widget(QFrame):
    def __init__(self, parent=None, layout=None):
        super().__init__(parent=parent)
        self.setLayout(layout)
        self.setObjectName(str(uuid.uuid4()))


class QFluentWindow(FluentWindow, EnginePart):
    name = "FluentWindow"
    just_shown = False  # To be used for any first launch logic: center()...
    onShownEvent = None
    onResizeEvent = None
    onCloseEvent = None
    onResizeEvent = None

    def __init__(self, kwargs={}):
        super().__init__()

        # setTheme(Theme.DARK if theme.lower() == "dark" else Theme.LIGHT)

        if self.__isWin11():
            self.windowEffect.setMicaEffect(self.winId(), isDarkTheme())

        if "icon" in kwargs:
            self.setIcon(kwargs["icon"]) if "icon" in kwargs else None

        if "title" in kwargs:
            self.setTitle(kwargs["title"])

        if "size" in kwargs:
            try:
                width, height = kwargs["size"].values()
                self.setSize(width, height)
            except ValueError as ex:
                self.setSize(500, 500)

    # add items to the side menu (drawer)
    def addNavInterface(self, layout, icon, title):
        self.homeInterface = Widget(parent=self, layout=layout)
        self.addSubInterface(self.homeInterface, icon, title)

    def addNavInterfaceSeparator(self):
        self.navigationInterface.addSeparator()

    def __isWin11(self):
        return sys.platform == "win32" and sys.getwindowsversion().build >= 22000

    def center(self):
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def setIcon(self, icon):
        self.setWindowIcon(QIcon(icon))

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setIcon(self, icon):
        self.setWindowIcon(QIcon(icon))

    def setSize(self, width, height):
        self.resize(width, height)

    def setLocation(self, x, y):
        self.move(x, y)

    # Events ----------------------
    def setOnShown(self, func):
        self.onShownEvent = func

    def showEvent(self, event):
        self.center()
        if self.onShownEvent:
            self.onShownEvent(self)

    def setOnClose(self, func):
        self.onCloseEvent = func

    # event has: ignore and accept
    def closeEvent(self, event):
        if self.onCloseEvent:
            self.onCloseEvent(self, event)

    def setOnResize(self, func):
        self.onResizeEvent = func

    # Removing the super() makes the system buttons appear misaligned
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.onResizeEvent:
            self.onResizeEvent(self)

    # ---------------------- Events

    def show(self):
        super().show()
