from PySide6.QtWidgets import QFrame

from limekit.widgets.base import LimeWidget


class HLine(LimeWidget, QFrame):
    __lime__ = "ui.HLine"

    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
