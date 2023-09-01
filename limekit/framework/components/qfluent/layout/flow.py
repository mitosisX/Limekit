from limekit.framework.core.engine.parts import EnginePart
from qfluentwidgets import FlowLayout
from PySide6.QtCore import Qt


class FlowLayout(FlowLayout, EnginePart):
    def __init__(self, parent=None):
        super().__init__(parent)

    def setSize(self, width, height):
        self.resize(width, height)

    def setContentAlignment(self, alignment):
        align = None
        selected_area = alignment.lower()

        if selected_area == "left":
            align = Qt.AlignLeft
        elif selected_area == "vcenter":
            align = Qt.AlignVCenter
        elif selected_area == "justify":
            align = Qt.AlignJustify

        self.setAlignment(align)

    def addChild(self, child):
        self.addWidget(child)

    def addChildren(self, *children):
        for eachChild in children:
            self.addWidget(eachChild)
