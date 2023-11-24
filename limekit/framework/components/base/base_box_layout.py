from PySide6.QtWidgets import QBoxLayout
from PySide6.QtCore import Qt


class BaseBoxLayout:
    def __init__(self, layout):
        self.layout = layout

    def addChild(self, child):
        self.layout.addWidget(child)

    def setMargins(self, left, top, right, bottom):
        self.layout.setContentsMargins(left, top, right, bottom)

    def setContentAlignment(self, *alignments):
        qt_alignments = {
            "leading": Qt.AlignmentFlag.AlignLeading,
            "alignLeft": Qt.AlignmentFlag.AlignLeft,
            "tight": Qt.AlignmentFlag.AlignRight,
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

        self.layout.setAlignment(sel_alignments)

    def addLayout(self, lay):
        self.layout.addLayout(lay)

    # This adds a QSpacerItem to the bottom of a VLayout and to the left of a HLayout
    def addStretch(self, stretch=1):
        self.layout.addStretch(stretch)
