from limekit.framework.core.engine.parts import EnginePart
from qfluentwidgets import CardWidget
from PySide6.QtWidgets import QHBoxLayout


class Card(CardWidget, EnginePart):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.hBoxLayout = QHBoxLayout(self)

        self.setFixedSize(360, 90)
