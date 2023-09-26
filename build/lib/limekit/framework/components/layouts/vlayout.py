from PySide6.QtWidgets import QVBoxLayout
from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtCore import Qt


class VerticalLayout(QVBoxLayout, EnginePart):
    name = "VLayout"

    def __init__(self, parent=None):
        super().__init__(parent)

    def addChild(self, child, stretch=0):
        self.addWidget(child, stretch)

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

    def addLayouts(self, *layouts):
        for layout in layouts:
            self.addLayout(layout)

    def addLayout(self, lay):
        super().addLayout(lay)

    def addElasticity(self, stretch=0):
        self.addStretch(stretch)
