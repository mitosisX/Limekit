from PySide6.QtWidgets import QStackedLayout
from limekit.framework.core.engine.parts import EnginePart


class StackedLayout(QStackedLayout, EnginePart):
    def __init__(self):
        super().__init__(parent=None)

    # This is a Grid layout; every child widget is positioned
    # x and y
    # xPos, yPos -> x position and y position respecitively
    # rows, columns -> number of rows and columns to span
    def addChild(self, child):
        self.addWidget(child)

    def addLayout(self, layout):
        super().addChildLayout(layout)

    # Also acts as the padding
    def setMargins(self, left, top, right, bottom):
        self.setContentsMargins(left, top, right, bottom)

    def setCurrentIndex(self, index):
        super().setCurrentIndex(index)
