from PySide6.QtWidgets import QSplitter, QWidget
from PySide6.QtCore import Qt
from limekit.framework.core.engine.parts import EnginePart


class Segmenter(QSplitter, EnginePart):
    def __init__(self, orientation="vertical"):
        super().__init__(
            Qt.Vertical if orientation.lower() == "vertical" else Qt.Horizontal
        )

    def addChild(self, child):
        self.addWidget(child)

    def addLayout(self, layout):
        widget = QWidget()
        widget.setLayout(layout)
        self.addChild(widget)
