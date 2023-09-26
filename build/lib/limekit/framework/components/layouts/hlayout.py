from PySide6.QtWidgets import QHBoxLayout
from limekit.framework.core.engine.parts import EnginePart


class HorizontalLayout(QHBoxLayout, EnginePart):
    name = "HLayout"

    def __init__(self, parent=None):
        super().__init__(parent)

    def addChild(self, *children):
        for eachChild in children:
            self.addWidget(eachChild)

    def addLayouts(self, *layouts):
        for layout in layouts:
            self.addLayout(layout)
