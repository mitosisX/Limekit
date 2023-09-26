from PySide6.QtWidgets import QHBoxLayout
from limekit.framework.core.engine.parts import EnginePart


class HorizontalLayout(QHBoxLayout, EnginePart):
    name = "HLayout"

    def __init__(self, parent=None):
        super().__init__(parent)

    def addChild(self, child, stretch=0):
        self.addWidget(child, stretch)

    def addLayouts(self, *layouts):
        for layout in layouts:
            self.addLayout(layout)
