"""Tabbed container.

`addTab`/`setCurrentIndex`/`setTabText`/etc. all take a Qt-native, 0-indexed
position, so none of them can be declared as a `Prop` -- a Prop has no way
to translate an index argument. A `currentIndex` Prop would also collide:
its generated setter would be named `setCurrentIndex`, exactly the name of
the *real* Qt method it would need to wrap, and once a hand-written
1-indexed `setCurrentIndex` already lives on the class the collision guard
correctly refuses to let the generated one land on top of it. Every
row/column-shaped accessor here is hand-written for the same reason
`ListBox` hand-writes its row accessors instead of using Prop.

`onTabChange`/`onTabClose` also can't use the declarative `Event` spec as-is:
Qt's `currentChanged`/`tabCloseRequested` signals pass a 0-indexed position,
and translating that to 1-indexed before it reaches Lua needs a real
wrapper, not a raw `connect`.
"""

from PySide6.QtWidgets import QTabWidget, QWidget

from limekit.kernel.bridge.guard import guard
from limekit.kernel.coerce import Icon, LuaIndex
from limekit.kernel.spec import Prop
from limekit.widgets.base import LimeWidget

_TAB_POSITIONS = {
    "top": QTabWidget.TabPosition.North,
    "bottom": QTabWidget.TabPosition.South,
    "left": QTabWidget.TabPosition.West,
    "right": QTabWidget.TabPosition.East,
}


def _tab_position(value):
    if not isinstance(value, str):
        return value
    try:
        return _TAB_POSITIONS[value.lower()]
    except KeyError:
        options = ", ".join(sorted(_TAB_POSITIONS))
        from limekit.kernel.errors import BridgeError
        raise BridgeError(f"unknown tab position {value!r}; expected one of: {options}") from None


class Tab(LimeWidget, QTabWidget):
    __lime__ = "ui.Tab"

    movable = Prop(bool, qt=("isMovable", "setMovable"))
    tabsClosable = Prop(bool, qt=("tabsClosable", "setTabsClosable"))
    tabPosition = Prop(object, qt=("tabPosition", "setTabPosition"), coerce=_tab_position)

    def __init__(self):
        super().__init__()
        self._onTabChange = None
        self._onTabClose = None
        self.currentChanged.connect(self._handleTabChange)
        self.tabCloseRequested.connect(self._handleTabClose)

    # -- structure -----------------------------------------------------

    def addTab(self, child, title, icon=None):
        """Qt native re-exposed: 1.x returned the new 0-indexed position,
        this returns `self` like every other Limekit builder method."""
        if icon:
            super().addTab(child, Icon(icon), str(title))
        else:
            super().addTab(child, str(title))
        return self

    def getChildAt(self, index):
        return self.widget(LuaIndex(index))

    def getIndexOf(self, child):
        return self.indexOf(child) + 1

    def removeTab(self, index):
        super().removeTab(LuaIndex(index))
        return self

    def getCount(self):
        return self.count()

    def setCurrentIndex(self, index):
        super().setCurrentIndex(LuaIndex(index))
        return self

    def getCurrentIndex(self):
        return self.currentIndex() + 1

    def setCurrentChild(self, child):
        self.setCurrentWidget(child)
        return self

    def setTabText(self, index, text):
        super().setTabText(LuaIndex(index), str(text))
        return self

    def getTabText(self, index):
        return self.tabText(LuaIndex(index))

    def setTabIcon(self, index, icon):
        super().setTabIcon(LuaIndex(index), Icon(icon))
        return self

    def setTabEnabled(self, index, enabled):
        super().setTabEnabled(LuaIndex(index), bool(enabled))
        return self

    def setTabVisible(self, index, visible):
        super().setTabVisible(LuaIndex(index), bool(visible))
        return self

    def setTabToolTip(self, index, tip):
        super().setTabToolTip(LuaIndex(index), str(tip))
        return self

    def setCornerChild(self, child):
        self.setCornerWidget(child)
        return self

    # -- events ----------------------------------------------------------

    def setOnTabChange(self, handler):
        self._onTabChange = guard(handler, widget="Tab", event="onTabChange")
        return self

    def _handleTabChange(self, index):
        if self._onTabChange:
            self._onTabChange(self, index + 1)

    def setOnTabClose(self, handler):
        self._onTabClose = guard(handler, widget="Tab", event="onTabClose")
        return self

    def _handleTabClose(self, index):
        if self._onTabClose:
            self._onTabClose(self, index + 1)


class TabItem(LimeWidget, QWidget):
    __lime__ = "ui.TabItem"

    layout = Prop(object, qt=("layout", "setLayout"))

    def __init__(self):
        super().__init__()
