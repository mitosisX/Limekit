from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QLayout, QWidget
from PySide6.QtCore import Qt
from typing import Union, Optional

class BaseLayout:
    """Base class for HorizontalLayout and VerticalLayout to reduce code duplication."""
    def __init__(self, parent: Optional[QWidget] = None):
        self._layout = self._create_layout()
        if parent:
            parent.setLayout(self._layout)

    def _create_layout(self) -> QLayout:
        """To be implemented by subclasses (returns QHBoxLayout or QVBoxLayout)."""
        raise NotImplementedError

    def addChild(self, child: Union[QWidget, QLayout], stretch: int = 0) -> None:
        """Adds a widget or nested layout to this layout."""
        if isinstance(child, QWidget):
            self._layout.addWidget(child, stretch)
        elif isinstance(child, QLayout):
            self._layout.addLayout(child)
        else:
            raise TypeError("Child must be a QWidget or QLayout.")

    def set_content_alignment(self, *alignments: str) -> None:
        """Sets alignment using human-readable strings (e.g., 'left', 'center')."""
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

        alignment_flags = 0
        for align in alignments:
            if align in qt_alignments:
                alignment_flags |= qt_alignments[align]
            else:
                raise ValueError(f"Invalid alignment: {align}")

        self._layout.setAlignment(alignment_flags)

    def set_margins(self, left: int, top: int, right: int, bottom: int) -> None:
        """Sets layout margins (acts as padding)."""
        self._layout.setContentsMargins(left, top, right, bottom)

    def set_spacing(self, spacing: int) -> None:
        """Sets spacing between widgets."""
        self._layout.setSpacing(spacing)

    def add_stretch(self, stretch: int = 1) -> None:
        """Adds stretch (spacer) to the layout."""
        self._layout.addStretch(stretch)

    def set_size_constraint_fixed(self) -> None:
        """Forces the layout to maintain a fixed size."""
        self._layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)