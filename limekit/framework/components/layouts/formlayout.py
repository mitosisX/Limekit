from PySide6.QtWidgets import QFormLayout
from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtCore import Qt


class FormLayout(QFormLayout, EnginePart):
    def __init__(self):
        super().__init__(parent=None)
        # self.setFieldGrowthPolicy(self.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        # self.setFormAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        # self.setLabelAlignment(Qt.AlignmentFlag.AlignJustify)

    def getLayout(self):
        return self.layout()

    def getAt(self, index):
        return self.takeAt(index - 1)

    # This is a Grid layout; every child widget is positioned
    # x and y
    # xPos, yPos -> x position and y position respecitively
    def addChild(self, title, child=None):
        # Use "" to avoid unwanted spacing
        # :addChild("", widget)
        # :addChild("Title", widget) NORMAL METHOD

        if isinstance(title, str):
            self.addRow(title, child)
        else:
            self.addRow(title)  # well, in this case, title is a widget ;-)

    def addLayout(self, title, layout):
        self.addRow(title, layout)

    def addChildren(self, *children):
        for eachChild in children:
            child = eachChild[0]
            xPos = eachChild[1]
            yPos = eachChild[2]

            self.addWidget(child, xPos, yPos)
