from limekit.framework.core.engine.app_engine import EnginePart
from qfluentwidgets import CommandBarView


class FluentCommandBar(CommandBarView, EnginePart):
    name = "CommandBar"

    def __init__(self, parent=None):
        super().__init__(parent)

    def setFitWidth(self):
        self.resizeToSuitableWidth()

    # The menu that appears as dropdown on the elipsis button
    def addExtraMenu(self, menu):
        self.addHiddenAction(menu)

    def addExtraMenus(self, *menus):
        for menu in menus:
            self.addHiddenAction(menu)
