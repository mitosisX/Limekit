from PySide6.QtWidgets import QWidget

class BaseLayout(QWidget):
    def addChild(self, child):
        self.addWidget(child)
        
    def addChildren(self, *children):
        for eachChild in children:            
            self.addWidget(eachChild)
            
    def addLayouts(self, *layouts):
        for layout in layouts:
            self.addLayout(layout)