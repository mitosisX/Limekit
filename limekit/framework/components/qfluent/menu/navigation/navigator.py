from limekit.framework.core.engine.app_engine import EnginePart
from PySide6.QtWidgets import QHBoxLayout, QLabel
from PySide6.QtCore import Qt


class Navigator(EnginePart):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(" ", "-"))
