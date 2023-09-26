from PySide6.QtWidgets import QSplitter
from PySide6.QtCore import Qt
from limekit.framework.core.engine.parts import EnginePart


class Segmenter(QSplitter, EnginePart):
    def __init__(self, orientation="vertical"):
        super().__init__(
            Qt.Vertical if orientation.lower() == "vertical" else Qt.Horizontal
        )

    def addChild(self, *children):
        for child in children:
            self.addWidget(child)
