from PySide6.QtWidgets import QBoxLayout

from limekit.layouts.base import BoxLayout


class VLayout(BoxLayout, QBoxLayout):
    """Stacks its children top to bottom."""

    __lime__ = "ui.VLayout"

    def __init__(self, parent=None):
        super().__init__(QBoxLayout.Direction.TopToBottom, parent)
