from PySide6.QtWidgets import QFormLayout
from limekit.framework.core.engine.parts import EnginePart

"""
OLayout is simply an Orientational Layout (OLayout)
Either Horizontal or Vertical
"""


class FormLayout(EnginePart, QFormLayout):
    def __init__(self):
        super().__init__()

    # This is a Grid layout; every child widget is positioned
    # x and y
    # xPos, yPos -> x position and y position respecitively
    def addChild(self, title, child):
        self.addRow(title, child)

    def addChildren(self, *children):
        for eachChild in children:
            child = eachChild[0]
            xPos = eachChild[1]
            yPos = eachChild[2]

            self.addWidget(child, xPos, yPos)
