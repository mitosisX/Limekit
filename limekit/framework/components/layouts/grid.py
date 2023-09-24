from PySide6.QtWidgets import QGridLayout
from limekit.framework.core.engine.parts import EnginePart

"""
OLayout is simply an Orientational Layout (OLayout)
Either Horizontal or Vertical
"""


class GridLayout(EnginePart, QGridLayout):
    def __init__(self, parent=None):
        super().__init__(parent)

    # This is a Grid layout; every child widget is positioned
    # x and y
    # xPos, yPos -> x position and y position respecitively
    # rows, columns -> number of rows and columns to span
    def addChild(self, child, xPos, yPos, rows=1, columns=1):
        self.addWidget(child, xPos, yPos, rows, columns)

    def addChildren(self, *children):
        for eachChild in children:
            child = eachChild[0]
            xPos = eachChild[1]
            yPos = eachChild[2]

            self.addWidget(child, xPos, yPos)

    def getChildAt(self, row, column):
        return self.itemAtPosition(row, column).widget()

    def offer(self):
        return self
