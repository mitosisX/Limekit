from PySide6.QtWidgets import QGridLayout
from limekit.framework.core.engine.parts import EnginePart


class GridLayout(QGridLayout, EnginePart):
    def __init__(self):
        super().__init__(parent=None)

    def getLayout(self):
        return self.layout()

    def getAt(self, index):
        return self.takeAt(index - 1)

    # This is a Grid layout; every child widget is positioned
    # x and y
    # xPos, yPos -> x position and y position respecitively
    # rows, columns -> number of rows and columns to span
    def addChild(self, child, xPos, yPos, rows=1, columns=1):
        self.addWidget(child, xPos, yPos, rows, columns)

    def addLayout(self, child, xPos, yPos, rows=1, columns=1):
        super().addLayout(child, xPos, yPos, rows, columns)

    def setSpacing(self, spacing):
        super().setSpacing(spacing)

    # Also acts as the padding
    def setMargins(self, left, top, right, bottom):
        self.setContentsMargins(left, top, right, bottom)

    def addChildren(self, *children):
        for eachChild in children:
            child = eachChild[0]
            xPos = eachChild[1]
            yPos = eachChild[2]

            self.addWidget(child, xPos, yPos)

    def getChildAt(self, row, column):
        return self.itemAtPosition(row, column).widget()

    # In PySide6, the setColumnStretch method is used to set the stretching
    # factor for a specific column in a QGridLayout or QFormLayout. This method allows
    # you to control how the columns of the layout expand or contract when the parent widget is resized.

    def setColumnStretch(self, column, stretch):
        super().setColumnStretch(column, stretch)
