from PySide6.QtWidgets import QMenu
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.components.controls.dockers.menu.menuitem import MenuItem


# Contains an arrow on it's side to show that it contains submenus
class Menu(QMenu, EnginePart):
    def __init__(self, title=None, parent=None):
        super().__init__(title=title, parent=parent)

    # menuitems
    # type: Menu
    def addMenuItems(self, *menus):
        for menu in menus:
            self.addAction(menu)

    def addMenuItem(self, menu):
        # print(menu.name)
        self.addAction(menu)

    def addDropMenu(self, menu):
        self.addMenu(menu)

    # To avoid redundancy in addMenuItem and addMenuItems, this functions shall handle all logic
    # def __determine_menutype_add_action(self, menu):
    #     if isinstance(menu, Menu):
    #         # print("Menu")
    #         self.addAction(menu)
    #     if isinstance(menu, MenuItem):
    #         print("MenuItem")

    #         self.addAction(menu)
    # print(type(menu))

    """
    Build menu from JSON template structure
    """

    def buildFromTemplate(self, template):
        self.fromTemplate(template, self)

    def fromTemplate(self, items, parent):
        for item in items.values():
            label = item["label"]

            if "submenu" in item:
                submenu = Menu(label)
                parent.addDropMenu(submenu)

                self.fromTemplate(item["submenu"], submenu)

                if "click" in item:
                    submenu.triggered.connect(item["click"])

                if "icon" in item:
                    submenu.setImage(item["icon"])

            else:
                # label = item["label"]
                action = MenuItem(label, self)

                if "-" in label:
                    self.addSeparator()

                if "accelerator" in item or "shortcut" in item:
                    action.setShortcut(item["accelerator"] or item["shortcut"])

                if "click" in item:
                    action.triggered.connect(item["click"])

                if "icon" in item:
                    action.setImage(item["icon"])

                if "name" in item:
                    self.addToObject(item["name"], action)

                parent.addMenuItem(action)
