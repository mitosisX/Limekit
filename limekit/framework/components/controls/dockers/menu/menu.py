from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QIcon
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.components.controls.dockers.menu.menuitem import MenuItem


# Contains an arrow on it's side to show that it contains submenus
class Menu(QMenu, EnginePart):
    objects = {}

    onClickFunction = None

    def __init__(self, title=None, parent=None):
        super().__init__(title=title, parent=parent)
        self.triggered.connect(self.__handleOnClick)

    def __handleOnClick(self):
        if self.onClickFunction:
            self.onClickFunction(self)

    def setOnClick(self, onClickFunction):
        self.onClickFunction = onClickFunction

    # menuitems
    # type: Menu
    def addMenuItems(self, *menus):
        for menu in menus:
            self.addAction(menu)

    def addMenuItem(self, menu):
        self.addAction(menu)

    # Another menu item
    def addDropMenu(self, menu):
        self.addMenu(menu)

    def setIcon(self, path):
        super().setIcon(QIcon(path))

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
        for key, item in template.items():
            label = item.label

            if "submenu" in item:
                menu = Menu(label)

                if "icon" in item:
                    menu.setIcon(item["icon"])

                self.addDropMenu(menu)

                self.fromTemplate(item.submenu, menu)
            else:
                self.template_add_menu_item(item, self)

    def fromTemplate(self, items, parent):
        for item in items.values():
            label = item["label"]

            if "submenu" in item:
                submenu = Menu(label)
                parent.addDropMenu(submenu)

                # if "name" in item:
                #     self.addToObject(item["name"], parent)

                self.fromTemplate(item["submenu"], submenu)

            else:
                # label = item["label"]

                self.template_add_menu_item(item, parent)

                # action = MenuItem(label, self)

                # if "-" in label:
                #     self.addSeparator()

                # if "accelerator" in item or "shortcut" in item:
                #     action.setShortcut(item["accelerator"] or item["shortcut"])

                # if "click" in item:
                #     action.setOnClick(item["click"])

                # if "icon" in item:
                #     action.setIcon(item["icon"])

                # if "name" in item:
                #     self.addToObject(item["name"], action)

                # parent.addMenuItem(action)

    def template_add_menu_item(self, item, parent):
        label = item["label"]

        action = MenuItem(label, self)

        if "-" in label:
            self.addSeparator()

        if "click" in item:
            action.setOnClick(item["click"])

        if "accelerator" in item or "shortcut" in item:
            action.setShortcut(item["accelerator"] or item["shortcut"])

        if "icon" in item:
            action.setIcon(item["icon"])

        if "extra" in item:
            # action.addMenuItem(item["extra"])
            print(item["extra"])

        if "name" in item:
            self.addToObject(item["name"], action)

        parent.addMenuItem(action)

        # def buildFromTemplate(self, template):
        #     self.fromTemplate(template, self)

        # def fromTemplate(self, items, parent):
        # for item in items.values():
        #     label = item["label"]
        #     if "submenu" in item:
        #         submenu = Menu(label)
        #         parent.addDropMenu(submenu)

        #         if "icon" in item:
        #             submenu.setIcon(item["icon"])

        #         if "name" in item:
        #             self.addToObject(item["name"], parent)

        #         self.fromTemplate(item["submenu"], submenu)

        #     else:
        #         # label = item["label"]
        #         action = MenuItem(label, self)

        #         if "-" in label:
        #             self.addSeparator()

        #         if "accelerator" in item or "shortcut" in item:
        #             action.setShortcut(item["accelerator"] or item["shortcut"])

        #         if "click" in item:
        #             action.setOnClick(item["click"])

        #         if "icon" in item:
        #             action.setIcon(item["icon"])

        #         if "name" in item:
        #             self.addToObject(item["name"], action)

        #         parent.addMenuItem(action)

    def addToObject(self, name, obj):
        self.objects.update({name: obj})
