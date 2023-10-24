from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QStackedWidget, QFrame, QHBoxLayout, QLabel
import sys

import qfluentwidgets
from limekit.framework.handle.theming.themes.qss.fluent_window.theme import (
    Theme as WindowQss,
)

from qfluentwidgets import (
    MSFluentTitleBar,
    isDarkTheme,
    FluentWindow,
    FluentIcon as FIF,
    setTheme,
    Theme,
    SplitFluentWindow,
    NavigationInterface,
    NavigationItemPosition,
    PopUpAniStackedWidget,
)

from qframelesswindow import TitleBar


def isWin11():
    return sys.platform == "win32" and sys.getwindowsversion().build >= 22000


# if isWin11():
#     from qframelesswindow import AcrylicWindow as Window
# else:
#     from qframelesswindow import FramelessWindow as Window
from qframelesswindow import AcrylicWindow as Window


class CustomTitleBar(TitleBar):
    """Title bar with icon and title"""

    def __init__(self, parent):
        super().__init__(parent)
        # add window icon
        self.iconLabel = QLabel(self)
        self.iconLabel.setFixedSize(18, 18)
        self.hBoxLayout.insertSpacing(0, 10)
        self.hBoxLayout.insertWidget(
            1, self.iconLabel, 0, Qt.AlignLeft | Qt.AlignBottom
        )
        self.window().windowIconChanged.connect(self.setIcon)

        # add title label
        self.titleLabel = QLabel(self)
        self.hBoxLayout.insertWidget(
            2, self.titleLabel, 0, Qt.AlignLeft | Qt.AlignBottom
        )
        self.titleLabel.setObjectName("titleLabel")
        self.window().windowTitleChanged.connect(self.setTitle)

    def setTitle(self, title):
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def setIcon(self, icon):
        self.iconLabel.setPixmap(QIcon(icon).pixmap(18, 18))


class QFluentWindow(Window, EnginePart):
    name = "FluentWindow"
    just_shown = False  # To be used for any first launch logic: center()...
    onShownEvent = None
    onResizeEvent = None
    onCloseEvent = None
    onResizeEvent = None

    def __init__(self, title="Limekit - lua framework", theme="dark"):
        super().__init__()

        self.setTitleBar(CustomTitleBar(self))

        setTheme(Theme.DARK if theme.lower() == "dark" else Theme.LIGHT)

        if self.__isWin11():
            self.windowEffect.setMicaEffect(self.winId(), isDarkTheme())

        # self.layout_ = QWidget(self)

        self.hBoxLayout = QHBoxLayout(self)

        # Holds the menu items on the left side
        # self.navigationInterface = NavigationInterface(self, showMenuButton=True)

        # User content goes in here
        self.stackWidget = PopUpAniStackedWidget(self)

        # self.setSize(500, 300)
        # self.__initLayout()
        self.__initWindow()

        self.setTitle(title)

    def addMenu(self, title, icon, widget):
        self.__addSubInterface(widget, icon, title)
        self.navigationInterface.addSeparator()

    def __initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def __initWindow(self):
        the_theme = WindowQss.getTheme()
        self.setStyleSheet(the_theme)

        self.titleBar.setAttribute(Qt.WA_StyledBackground)

    def __addSubInterface(
        self,
        interface,
        icon,
        text: str,
        position=NavigationItemPosition.TOP,
        parent=None,
        where="",
    ):
        # if where.lower() == "bottom":
        #     position = NavigationItemPosition.BOTTOM

        """add sub interface"""
        mainLay = QWidget(self)
        # mainLay.setContentsMargins(30, 60, 30, 30)
        # mainLay.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        # mainLay.setSpacing(6)
        mainLay.setLayout(interface)

        self.stackWidget.addWidget(mainLay)

        self.navigationInterface.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.__switchTo(interface),
            position=position,
            tooltip=text,
            parentRouteKey=parent.objectName() if parent else None,
        )

    def __switchTo(self, interface):
        self.stackWidget.setCurrentWidget(interface)

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

    def addChild(self, child):
        self.hBoxLayout.addWidget(child)

    def setMainLayout(self, layout):
        self.hBoxLayout.addLayout(layout)

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
            self.hBoxLayout.addLayout(layout)

    def addLayout(self, lay):
        self.hBoxLayout.addLayout(lay)

    def setIcon(self, icon):
        self.setWindowIcon(QIcon(icon))

    def setMainLayout(self, layout):
        pass

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
