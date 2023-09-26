from PySide6.QtWidgets import QMenuBar
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.components.controls.dockers.menu.menuitem import MenuItem


"""
Structure for creating a Menubar
    Menubar
        - Menu                  (File, Edit, View, Help)
            MenuItems           (New File, Open File, Exit)
"""


class Menubar(QMenuBar, EnginePart):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    # menus
    # type: Menu
    def addMenuItem(self, menu):
        self.addMenu(menu)

    def addMenuItems(self, *menus):
        for menu in menus:
            self.addMenu(menu)

    # This method isn't working, total waste of time
    def create_menu(self, menu_structure):
        items = []
        for item in menu_structure:
            if "type" in item and item["type"] == "separator":
                menu_item = MenuItem("Hey")
                # menu_item.setSeparator(True)
                items.append(menu_item)
            else:
                menu_item = MenuItem(item["label"])
                if "submenu" in item:
                    submenu_items = self.create_menu(item["submenu"])
                    for submenu_item in submenu_items:
                        # items.push(submenu_item)
                        continue
                else:
                    continue
                    if "click" in item:
                        menu_item.click = item["click"]
                    if "accelerator" in item:
                        menu_item.accelerator = item["accelerator"]
                    if "role" in item:
                        menu_item.role = item["role"]
                items.append(menu_item)

        # print(items)
        return items
