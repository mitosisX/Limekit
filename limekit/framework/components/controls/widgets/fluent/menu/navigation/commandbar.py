from limekit.framework.core.engine.app_engine import EnginePart
from qfluentwidgets import CommandBarView
from PySide6.QtCore import Qt

# This works best with Flyout
"""
command = CommandBar(window)

laptop = MenuItem()
laptop.setImage(images('laptop.png'))
command.addAction(laptop)

command.addSeparator()
command.addAction(laptop)

hid1 = MenuItem('hidden menu1')
hid1.setImage(images('hidden menu.png'))

command.addExtraMenu(hid1)
command:setFitWidth()

fly = Flyout(window, command)
fly:show(sender, anim)
"""


class FluentCommandBar(CommandBarView, EnginePart):
    name = "CommandBar"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

    def setFitWidth(self):
        self.resizeToSuitableWidth()

    # The menu that appears as dropdown on the elipsis button
    def addExtraMenu(self, menu):
        self.addHiddenAction(menu)

    def addExtraMenus(self, *menus):
        for menu in menus:
            self.addHiddenAction(menu)
