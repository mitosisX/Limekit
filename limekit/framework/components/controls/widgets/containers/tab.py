from PySide6.QtWidgets import QTabWidget
from PySide6.QtGui import QPixmap

from limekit.framework.core.engine.parts import EnginePart

from PySide6.QtGui import QIcon

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

    def __init__(self):
        super().__init__()
        self.tabCloseRequested.connect(self.__handleTabClosing)

    def setOnTabClose(self, onTabClosingFunc):
        self.onTabClosingFunc = onTabClosingFunc

    def __handleTabClosing(self, index):
        if self.onTabClosingFunc:
            self.onTabClosingFunc(self, index)

    def addTabs(self, *tabs):
        for eachTab in tabs:
            tab = eachTab[0]
            title = eachTab[1]

            self.addTab(tab, title)

    def removeTab(self, index):
        super().removeTab(index)

    def setVisibility(self, index, visibility):
        self.setTabVisible(index, visibility)

    def setTabsCloseable(self, closeable):
        super().setTabsClosable(closeable)

    def setPosition(self, position):
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

    def addTab(self, tab, title, icon=""):
        super().addTab(tab, QIcon(icon), title)

    def addTabitedm(self, tab, path, title):
        pixmap = QPixmap(path)
        # self.setScaledContents(True)
        self.setPixmap(pixmap)

        self.addTab(tab, pixmap, title)

    def getTabIndex(self):
        return self.currentIndex
