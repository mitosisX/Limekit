from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtWidgets import QFrame


class VLine(QFrame, EnginePart):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
