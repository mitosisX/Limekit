from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSplitter, QWidget
from limekit.framework.core.engine.parts import EnginePart


class Splitter(QSplitter, EnginePart):
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

    def setHandleWidth(self, width):
        super().setHandleWidth(width)

    def setOrientation(self, orientation):
        super().setOrientation(
            Qt.Vertical if orientation.lower() == "vertical" else Qt.Horizontal
        )

    def setSize(self, width, height):
        self.resize(width, height)

    def setMinHeight(self, height):
        self.setMinimumHeight(height)

    def setMaxHeight(self, height):
        self.setMaximumHeight(height)

    def setMinWidth(self, width):
        self.setMinimumWidth(width)

    def setMaxWidth(self, width):
        self.setMaximumWidth(width)
