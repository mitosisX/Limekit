from PySide6.QtGui import QIcon
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QTabWidget

from limekit.engine.parts import EnginePart
from limekit.components.widgets.containers.tabitem import TabItem
from limekit.components.widgets.containers.tabbar import TabBar
from limekit.components.base.widget_base import BaseWidget

"""
Functions available in PySide6 documentation
    - Only those I could understand weren't removed from below

def setTabsClosable(bool)
def changeEvent(self, arg__1: PySide6.QtCore.QEvent) -> None: ...
def count(self) -> int: ...
def currentIndex(self) -> int: ...
def event(self, arg__1: PySide6.QtCore.QEvent) -> bool: ...
def iconSize(self) -> PySide6.QtCore.QSize: ...
def insertTab(self, index: int, widget: PySide6.QtWidgets.QWidget, arg__3: str) -> int: ...
def isTabEnabled(self, index: int) -> bool: ...
def isTabVisible(self, index: int) -> bool: ...
def setCurrentIndex(self, index: int) -> None: ...
def setIconSize(self, size: PySide6.QtCore.QSize) -> None: ...
def setMovable(self, movable: bool) -> None: ...
def setTabBar(self, arg__1: PySide6.QtWidgets.QTabBar) -> None: ...
def setTabEnabled(self, index: int, enabled: bool) -> None: ...
def setTabIcon(self, index: int, icon: Union[PySide6.QtGui.QIcon, PySide6.QtGui.QPixmap]) -> None: ...
def setTabPosition(self, position: PySide6.QtWidgets.QTabWidget.TabPosition) -> None: ...
def setTabShape(self, s: PySide6.QtWidgets.QTabWidget.TabShape) -> None: ...
def setTabText(self, index: int, text: str) -> None: ...
def setTabToolTip(self, index: int, tip: str) -> None: ...
def setTabVisible(self, index: int, visible: bool) -> None: ...
def setTabsClosable(self, closeable: bool) -> None: ...
def showEvent(self, arg__1: PySide6.QtGui.QShowEvent) -> None: ...
def tabsClosable(self) -> bool: ...
"""


class Tab(QTabWidget, EnginePart):
    onTabClosingFunc = None
    onTabChangeFunc = None
    onTabMovedFunc = None

    def __init__(self):
        super().__init__()

        self.tabCloseRequested.connect(self.__handleTabClosing)
        self.currentChanged.connect(self.__handleTabChange)
        self.tabBar().tabMoved.connect(self.__handleTabMoved)
        # self.setTabBar(TabBar())

    def setOnTabMoved(self, onTabMovedFunc):
        self.onTabMovedFunc = onTabMovedFunc

    def __handleTabMoved(self, from_index, to_index):
        if self.onTabMovedFunc:
            self.onTabMovedFunc(self, from_index, to_index)

    def setOnTabClose(self, onTabClosingFunc):
        self.onTabClosingFunc = onTabClosingFunc

    def __handleTabClosing(self, index):
        if self.onTabClosingFunc:
            self.onTabClosingFunc(self, index)

    def setOnTabChange(self, onTabChangeFunc):
        self.onTabChangeFunc = onTabChangeFunc

    def __handleTabChange(self, index):
        if self.onTabChangeFunc:
            self.onTabChangeFunc(self, index + 1)

    def addTabs(self, *tabs):
        for eachTab in tabs:
            tab = eachTab[0]
            title = eachTab[1]

            self.addTab(tab, title)

    # Adds a widgets to the corner to a tab
    def setCornerChild(self, child):
        self.setCornerWidget(child)

    def getChildAt(self, index):
        return self.widget(index - 1)

    def setMovable(self, movable):
        return super().setMovable(movable)

    def setTabIcon(self, index, icon: str | QIcon):
        if isinstance(icon, str):
            super().setTabIcon(index - 1, QIcon(icon))

        elif isinstance(icon, QIcon):
            super().setTabIcon(index - 1, icon)

    def setTabText(self, index, title):
        super().setTabText(
            index - 1,
            title,
        )

    def getTabText(self, index):
        return super().tabText(index - 1)

    def setStyle(self, style):
        self.setStyleSheet(style)

    def removeTab(self, index):
        super().removeTab(index - 1)

    def getIndexOf(self, widget):
        return self.indexOf(widget) + 1

    def setVisibility(self, index, visibility):
        self.setTabVisible(index, visibility)

    def setTabsCloseable(self, closeable):
        super().setTabsClosable(closeable)

    def setTabsPosition(self, position):
        positions = {
            "left": QTabWidget.TabPosition.West,
            "top": QTabWidget.TabPosition.North,
            "right": QTabWidget.TabPosition.East,
            "bottom": QTabWidget.TabPosition.South,
        }

        self.setTabPosition(
            positions[position] if positions.get(position) else positions["top"]
        )

    def setToolTip(self, index, tooltip):
        self.setTabToolTip(index, tooltip)

    def addTab(self, tab: TabItem, title, icon=""):
        return super().addTab(tab, QIcon(icon), title) + 1

    def setCurrentIndex(self, index):
        super().setCurrentIndex(index - 1)

    def getCurrentIndex(self):
        return self.currentIndex() + 1

    def setCurrentChild(self, tab):
        self.setCurrentWidget(tab)

    def getCount(self):
        return self.count()
