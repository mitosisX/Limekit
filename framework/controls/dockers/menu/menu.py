from PySide6.QtWidgets import QMenu
from framework.controls.dockers.menu.menuitem import MenuItem

class Menu(QMenu):
    def __init__(self, text = None):
        super().__init__(text)

    # menuitems
    # type: MenuItem
    def addItems(self, *menuitems):
        for menuitem in menuitems:
            self.addAction(menuitem)
            
    def addItem(self, menuitem):
        self.addAction(menuitem)
            
    """
    Build menu from JSON template structure
    """
    def fromTemplate(self, template):
        menus = self.create_menu(template)
        
        for menu in menus:
            self.addAction(menu)
        # self.addItem(menus)
            
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
