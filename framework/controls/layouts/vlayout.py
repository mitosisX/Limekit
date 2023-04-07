from PySide6.QtWidgets import QVBoxLayout

"""
OLayout is simply an Orientational Layout (OLayout)
Either Horizontal or Vertical
"""

class VerticalLayout(QVBoxLayout):
    def __init__(self):
        super().__init__()
    
    def addChild(self, child):
        self.addWidget(child)
        
    def addChildren(self, *children):
        for eachChild in children:            
            self.addWidget(eachChild)