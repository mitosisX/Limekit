from PySide6.QtWidgets import QHBoxLayout
from limekit.framework.core.engine.parts import EnginePart


"""
OLayout is simply an Orientational Layout (OLayout)
Either Horizontal or Vertical
"""


class HorizontalLayout(EnginePart, QHBoxLayout):
    name = "HLayout"

    def __init__(self):
        super().__init__()

    def addChild(self, child):
        self.addWidget(child)

    def addChildren(self, *children):
        for eachChild in children:
            self.addWidget(eachChild)

    def addLayouts(self, *layouts):
        for layout in layouts:
            self.addLayout(layout)
