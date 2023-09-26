from PySide6.QtWidgets import QFormLayout
from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtCore import Qt

"""
OLayout is simply an Orientational Layout (OLayout)
Either Horizontal or Vertical
"""


class FormLayout(QFormLayout, EnginePart):
    def __init__(self):
        super().__init__()
        # self.setFieldGrowthPolicy(self.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        # self.setFormAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        # self.setLabelAlignment(Qt.AlignmentFlag.AlignJustify)

    # This is a Grid layout; every child widget is positioned
    # x and y
    # xPos, yPos -> x position and y position respecitively
    def addChild(self, title, child):
        # Use "" to avoid unwanted spacing
        # :addChild("", widget)
        # :addChild("Title", widget) NORMAL METHOD
        if not title:
            self.addRow(child)
        else:
            self.addRow(title, child)

    def addChildren(self, *children):
        for eachChild in children:
            child = eachChild[0]
            xPos = eachChild[1]
            yPos = eachChild[2]

            self.addWidget(child, xPos, yPos)
