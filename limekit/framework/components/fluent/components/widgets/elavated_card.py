from PySide6.QtCore import Qt
from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import (
    CaptionLabel,
    ElevatedCardWidget,
    ImageLabel,
)


class FElevatedCard(ElevatedCardWidget, EnginePart):
    def __init__(self):
        super().__init__(parent=None)

        self.main_layout = QVBoxLayout(self)

        self.setFixedSize(168, 176)

    def addChild(self, widget):
        self.main_layout.addWidget(widget)
