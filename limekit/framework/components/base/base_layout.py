from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout
from limekit.framework.components.controls.widgets.spacer import Spacer


class BaseLayout(QBoxLayout):
    """Base class for all layout wrappers"""

    # Common alignment constants
    ALIGNMENTS = {
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

    def __init__(self, direction: QBoxLayout.Direction, parent=None):
        super().__init__(direction, parent)

    def addLayout(self, layout, stretch=0):
        return super().addLayout(layout, stretch)

    def getLayoutAt(self, index):
        return self.itemAt(index - 1).layout()

    def getChildAt(self, index):
        return self.itemAt(index - 1).widget()

    # Counts all children available in the layout
    def getCount(self):
        return self.count()

    def getLayout(self):
        return self.layout()

    def addSpacer(self, spacer: Spacer):
        self.addSpacerItem(spacer)

    def addStretch(self, stretch=1):
        super().addStretch(stretch)

    def setSpacing(self, spacing):
        super().setSpacing(spacing)

    def setMargins(self, left, top, right, bottom):
        self.setContentsMargins(left, top, right, bottom)

    # Common methods
    def addChild(self, child, stretch=0):
        """Add a widget or layout with optional stretch"""
        self.addWidget(child, stretch)

    def setContentAlignment(self, *alignments):
        """Set alignment using string flags"""
        alignment = 0
        for align in alignments:
            if align in self.ALIGNMENTS:
                alignment |= self.ALIGNMENTS[align]
        self.setAlignment(alignment)

    def clear(self):
        """Remove all items from layout"""
        while self.count():
            item = self.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
