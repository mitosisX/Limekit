from PySide6.QtWidgets import QFrame

from limekit.widgets.base import LimeWidget


class VLine(LimeWidget, QFrame):
    __lime__ = "ui.VLine"

    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
