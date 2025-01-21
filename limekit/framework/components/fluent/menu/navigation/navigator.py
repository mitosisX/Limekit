from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel


class Navigator(EnginePart):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignmentFlag.AlignCenter)
        self.setObjectName(text.replace(" ", "-"))
