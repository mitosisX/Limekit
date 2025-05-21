from limekit.engine.parts import EnginePart
from PySide6.QtWidgets import QFrame


class HLine(QFrame, EnginePart):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
