from PySide6.QtWidgets import QBoxLayout

from limekit.layouts.base import BoxLayout


class HLayout(BoxLayout, QBoxLayout):
    """Arranges its children left to right."""

    __lime__ = "ui.HLayout"

    def __init__(self, parent=None):
        super().__init__(QBoxLayout.Direction.LeftToRight, parent)
