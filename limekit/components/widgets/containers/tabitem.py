from PySide6.QtWidgets import QWidget
from limekit.engine.parts import EnginePart


class TabItem(QWidget, EnginePart):
    def __init__(self):
        super().__init__()

    def setLayout(self, child):
        super().setLayout(child)
