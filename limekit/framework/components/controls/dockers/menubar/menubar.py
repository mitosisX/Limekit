from PySide6.QtWidgets import QMenuBar
from PySide6.QtGui import QFont
from limekit.framework.core.engine.parts import EnginePart

from limekit.framework.components.controls.dockers.menu.menu import Menu
from limekit.framework.components.controls.dockers.menu.menuitem import MenuItem
import lupa

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu

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

    def addDropMenu(self, menu):
        self.addMenu(menu)

    def addMenuItems(self, *menus):
        for menu in menus:
            self.addMenu(menu)

    def buildFromTemplate(self, template):
        self.fromTemplate(template, self)

    def fromTemplate(self, items, parent):
        for item in items.values():
            label = item["label"]
            if "submenu" in item:
                submenu = Menu(label)
                parent.addDropMenu(submenu)
                self.fromTemplate(item["submenu"], submenu)

                # self.addToObject(label, submenu)
            else:
                # label = item["label"]
                action = MenuItem(label, self)

                if "-" in label:
                    self.addSeparator()

                if "accelerator" in item:
                    action.setShortcut(item["accelerator"])

                if "click" in item:
                    action.triggered.connect(item["click"])

                if "icon" in item:
                    action.setImage(item["icon"])

                # self.addToObject(label, action)

                parent.addMenuItem(action)

    def addToObject(self, name, obj):
        self.objects.update(name, obj)

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
