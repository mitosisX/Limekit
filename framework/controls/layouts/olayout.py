from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout

"""
OLayout is simply an Orientational Layout (OLayout)
Either Horizontal or Vertical
"""

class OLayout:
    def __init__(self, _type = 'vertical'):
        self.layout = self.layoutType(_type)
        
    def layoutType(self, type): # Gets the type of layout
        if type.lower() == 'horizontal':
            return QHBoxLayout()
        elif type.lower() == 'vertical':
            return QVBoxLayout()
                 
    def addChild(self, child):
        self.layout.addWidget(child)
        
    def addChild(self, *children):
        for child in children:
            self.layout.addWidget(child)
            # self.layout.addStretch()       
        
    def addLayout(self, *children):
        for child in children:
            self.layout.addLayout(child.layout)
    
    def offer(self):
        return self.layout