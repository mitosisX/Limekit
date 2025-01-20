from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QStackedWidget, QFrame, QHBoxLayout, QLabel
import sys

import qfluentwidgets

from qfluentwidgets import (
    isDarkTheme,
    FluentIcon as FIF,
)

def isWin11():
    return sys.platform == "win32" and sys.getwindowsversion().build >= 22000


# if isWin11():
#     from qframelesswindow import AcrylicWindow as Window
# else:
#     from qframelesswindow import FramelessWindow as Window
from qfluentwidgets import FluentWindow


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

        # self.setSize(500, 300)
        # self.__initLayout()
        
        if "icon" in kwargs:
            self.setIcon(kwargs["icon"]) if "icon" in kwargs else None
            
        if "title" in kwargs:      
            self.setTitle(kwargs['title'])
            
        if "size" in kwargs:
            try:
                width, height = kwargs["size"].values()
                self.setSize(width, height)
            except ValueError as ex:
                self.setSize(500, 500)

    def __isWin11(self):
        return sys.platform == "win32" and sys.getwindowsversion().build >= 22000

    def center(self):
        # Old center() algo
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # desktop = QApplication.screens()[0].availableGeometry()
        # w, h = desktop.width(), desktop.height()
        # self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)


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
