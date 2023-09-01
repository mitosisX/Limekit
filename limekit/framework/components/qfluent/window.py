from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

import qfluentwidgets

from qfluentwidgets import (
    MSFluentTitleBar,
    isDarkTheme,
    FluentWindow,
    FluentIcon,
    setTheme,
    Theme,
    SplitFluentWindow,
)
from qframelesswindow import FramelessWindow, StandardTitleBar


class FluentWindow(FluentWindow, EnginePart):
    just_shown = False  # To be used for any first launch logic: center()...
    onShownEvent = None
    onResizeEvent = None
    onCloseEvent = None
    onResizeEvent = None

    def __init__(self, title="Limekit - lua framework"):
        super().__init__()
        self.setTitleBar(MSFluentTitleBar(self))
        self.windowEffect.setMicaEffect(self.winId(), isDarkTheme())

        self.layout_ = QVBoxLayout()
        self.widgetLayout.addLayout(self.layout_)

        # self.setSize(500, 300)

        self.setTitle(title)

    def center(self):
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def addChild(self, child):
        self.layout.addWidget(child)

    def setMainLayout(self, layout):
        self.layout_.addLayout(layout)

    def setContentAlignment(self, alignment):
        align = None
        selected_area = alignment.lower()

        if selected_area == "top":
            align = Qt.AlignLeft
        elif selected_area == "hcenter":
            align = Qt.AlignHCenter
        elif selected_area == "justify":
            align = Qt.AlignJustify

        self.setAlignment(align)

    def addChildren(self, *children):
        for eachChild in children:
            self.addWidget(eachChild)

    def addLayouts(self, *layouts):
        for layout in layouts:
            self.layout_.addLayout(layout)

    def addLayout(self, lay):
        self.layout_.addLayout(lay)

    def setIcon(self, icon):
        self.setWindowIcon(QIcon(icon))

    def setMainLayout(self, layout):
        pass

    def setTheme(self, theme):
        qfluentwidgets.setTheme(Theme.DARK if theme.lower() == "dark" else Theme.LIGHT)

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
