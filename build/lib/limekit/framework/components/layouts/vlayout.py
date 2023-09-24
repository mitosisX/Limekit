from PySide6.QtWidgets import QVBoxLayout
from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtCore import Qt


class VerticalLayout(EnginePart, QVBoxLayout):
    name = "VLayout"

    def __init__(self, parent=None):
        super().__init__(parent)

    def addChild(self, *child):
        self.addChildren(*child)

    def setContentAlignment(self, alignment):
        align = None
        selected_area = alignment.lower()

        if selected_area == "top":
            align = Qt.AlignLeft
        elif selected_area == "hcenter":
            align = Qt.AlignHCenter
        elif selected_area == "justify":
            align = Qt.AlignJustify

        self.setAlignment(align)

    def addChildren(self, *children):
        for eachChild in children:
            self.addWidget(eachChild)

    def addLayouts(self, *layouts):
        for layout in layouts:
            self.addLayout(layout)

    def addLayout(self, lay, fake=None):
        super().addLayout(lay)
