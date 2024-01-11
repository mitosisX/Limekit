from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout
from limekit.framework.core.engine.parts import EnginePart


class VerticalLayout(QVBoxLayout, EnginePart):
    name = "VLayout"

    def __init__(self, parent=None):
        super().__init__(parent)

    def addChild(self, child, stretch=0):
        self.addWidget(child, stretch)

    def setContentAlignment(self, *alignments):
        qt_alignments = {
            "leading": Qt.AlignmentFlag.AlignLeading,
            "left": Qt.AlignmentFlag.AlignLeft,
            "right": Qt.AlignmentFlag.AlignRight,
            "trailing": Qt.AlignmentFlag.AlignTrailing,
            "hcenter": Qt.AlignmentFlag.AlignHCenter,
            "justify": Qt.AlignmentFlag.AlignJustify,
            "absolute": Qt.AlignmentFlag.AlignAbsolute,
            "horizontal_mask": Qt.AlignmentFlag.AlignHorizontal_Mask,
            "top": Qt.AlignmentFlag.AlignTop,
            "bottom": Qt.AlignmentFlag.AlignBottom,
            "vcenter": Qt.AlignmentFlag.AlignVCenter,
            "center": Qt.AlignmentFlag.AlignCenter,
            "baseline": Qt.AlignmentFlag.AlignBaseline,
            "vertical_mask": Qt.AlignmentFlag.AlignVertical_Mask,
        }

        sel_alignments = 0

        for align in alignments:
            if qt_alignments.get(align):
                sel_alignments |= qt_alignments[align]

        self.setAlignment(sel_alignments)

    def addLayout(self, lay):
        super().addLayout(lay)

    # This adds a QSpacerItem to the bottom of a VLayout and to the left of a HLayout
    def addStretchi(self, stretch=1):
        super().addStretch(stretch)

    # Also acts as the padding
    def setMargins(self, left, top, right, bottom):
        self.setContentsMargins(left, top, right, bottom)
