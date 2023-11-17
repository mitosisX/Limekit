from PySide6.QtWidgets import QHBoxLayout
from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtCore import Qt


class HorizontalLayout(QHBoxLayout, EnginePart):
    name = "HLayout"

    def __init__(self):
        super().__init__(parent=None)

    def addChild(self, child, stretch=0):
        self.addWidget(child, stretch)

    def addLayout(self, lay):
        super().addLayout(lay)

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

    # def addLayouts(self, *layouts):
    #     for layout in layouts:
    #         self.addLayout(layout)

    def addExpansion(self, stretch=0):
        self.addStretch(stretch)

    # Also acts as the padding
    def setMargins(self, left, top, right, bottom):
        self.setContentsMargins(left, top, right, bottom)
