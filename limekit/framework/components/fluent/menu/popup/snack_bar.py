from qfluentwidgets import InfoBarManager, InfoBar, InfoBarPosition
from PySide6.QtCore import QPoint, Qt
from limekit.framework.core.engine.parts import EnginePart


@InfoBarManager.register("Custom")
class CustomInfoBarManager(InfoBarManager):
    """Custom info bar manager"""

    def _pos(self, infoBar: InfoBar, parentSize=None):
        p = infoBar.parent()
        parentSize = parentSize or p.size()

        # the position of first info bar
        x = (parentSize.width() - infoBar.width()) // 2
        y = (parentSize.height() - infoBar.height()) // 2

        # get the position of current info bar
        index = self.infoBars[p].index(infoBar)
        for bar in self.infoBars[p][0:index]:
            y += bar.height() + self.spacing

        return QPoint(x, y)

    def _slideStartPos(self, infoBar: InfoBar):
        pos = self._pos(infoBar)
        return QPoint(pos.x(), pos.y() - 16)


class SnackBar(EnginePart):
    title = ""
    content = ""
    icon = ""
    duration = 0
    position = ""
    parent = None

    def __init__(self, parent, title, content, icon, duration):
        self.parent = parent
        self.title = title
        self.content = content
        self.icon = icon
        self.duration = duration
        # self.position = position

    def show(self, type_=""):
        if type_ == "":
            InfoBar.new(
                icon=self.icon,
                title=self.title,
                content=self.content,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM,
                duration=self.duration,
                parent=self.parent,
            ).setCustomBackgroundColor("white", "#202020")

        elif type_ == "info":
            InfoBar(
                icon=self.icon,
                title=self.title,
                content=self.content,
                orient=Qt.Vertical,  # vertical layout
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=self.duration,
                parent=self.parent,
            ).show()
