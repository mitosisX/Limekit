import lupa
from PySide6.QtWidgets import QMenuBar, QMenu
from PySide6.QtGui import QFont, QAction

from limekit.engine.parts import EnginePart
from limekit.components.menu.menu import Menu
from limekit.components.menu.menuitem import MenuItem


# from PySide6.QtGui import QAction
# from PySide6.QtWidgets import QMenu


class Menubar(QMenuBar, EnginePart):
    objects = {}

    def __init__(self):
        super().__init__(parent=None)

    # menus
    # type: Menu
    def addMenuItem(self, menu):
        self.addAction(menu)

    def addMenu(self, menu):
        super().addMenu(menu)

    def addMenuItems(self, *menus):
        for menu in menus:
            self.addMenu(menu)

    def buildFromTemplate(self, template):
        for key, item in template.items():
            label = item.label

            menu = Menu(label)
            self.addMenu(menu)

            if "submenu" in item:
                self.fromTemplate(item.submenu, menu)

    def fromTemplate(self, items, parent):
        for item in items.values():
            label = item["label"]
            if "submenu" in item:
                submenu = Menu(label)

                parent.addMenu(submenu)

                if "name" in item:
                    self.addToObject(item["name"], parent)

                self.fromTemplate(item["submenu"], submenu)

            else:
                # label = item["label"]
                action = MenuItem(label, self)

                if "-" in label:
                    self.addSeparator()

                if "click" in item:
                    action.setOnClick(item["click"])

                if "accelerator" in item or "shortcut" in item:
                    action.setShortcut(item["accelerator"] or item["shortcut"])

                if "icon" in item:
                    action.setIcon(item["icon"])

                if "name" in item:
                    self.addToObject(item["name"], action)

                parent.addMenuItem(action)

    # Old implementation
    # def buildFromTemplate_(self, template):
    #     self.fromTemplate(template, self)

    def addToObject(self, name, obj):
        self.objects.update({name: obj})

    def getChild(self, child):
        return self.objects[child] or None

    def buildFromTemplate__(self, items, parent):
        for item in items.values():
            if "submenu" in item:
                # submenu here is of type DropMenu
                submenu = Menu(item["label"])
                # print(submenu)
                parent.addMenuItem(submenu)
                if parent != self:
                    self.addMenuItem(parent)

                self.buildFromTemplate_(item["submenu"], submenu)
            else:
                # action is of type
                action = MenuItem(item["label"])

                if "accelerator" in item:
                    action.setShortcut(item["accelerator"])
                # action.triggered.connect(item["click"])
                parent.addMenuItem(action)

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
