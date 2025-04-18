from PySide6.QtWidgets import QHBoxLayout, QLayout
from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtCore import Qt


class HorizontalLayout(QHBoxLayout):
    name = "HLayout"

    def __init__(self):
        super().__init__(parent=None)

    def addChild(self, child, stretch=0):
        self.addWidget(child, stretch)

    def addLayout(self, lay):
        super().addLayout(lay)

    def getCount(self):
        return self.count()

    def getAt(self, index):
        return self.takeAt(index - 1)

    def getLayout(self):
        return self.layout()

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

    def setSizeConstraint(self):
        return super().setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

    def addStretch(self, stretch=0):
        super().addStretch(stretch)

    # Also acts as the padding
    def setMargins(self, left, top, right, bottom):
        self.setContentsMargins(left, top, right, bottom)
