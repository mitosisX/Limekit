from PySide6.QtWidgets import QGridLayout

"""
OLayout is simply an Orientational Layout (OLayout)
Either Horizontal or Vertical
"""

class GridLayout(QGridLayout):
    def __init__(self):
        super().__init__()
    
    # This is a Grid layout; every child widget is positioned
    # x and y
    # xPos, yPos -> x position and y position respecitively
    def addChild(self, child, xPos, yPos):
        self.addWidget(child, xPos, yPos)
        
    def addChildren(self, *children):
        for eachChild in children:
            child = eachChild[0]
            xPos = eachChild[1]
            yPos = eachChild[2]
            
            self.addWidget(child, xPos, yPos)
            
    def offer(self):
        return self