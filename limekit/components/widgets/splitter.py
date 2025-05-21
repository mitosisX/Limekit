from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSplitter, QWidget
from limekit.engine.parts import EnginePart


class Splitter(QSplitter, EnginePart):
    def __init__(self, orientation="vertical"):
        super().__init__(
            Qt.Orientation.Vertical
            if orientation.lower() == "vertical"
            else Qt.Orientation.Horizontal
        )

    def addChild(self, child):
        self.addWidget(child)

    def addLayout(self, layout):
        widget = QWidget()
        widget.setLayout(layout)
        self.addChild(widget)

    def setSizes(self, sizes):
        super().setSizes(list(sizes.values()))

    def setHandleWidth(self, width):
        super().setHandleWidth(width)

    def setOrientation(self, orientation):
        orientation = orientation.lower()

        if orientation == "horizontal":
            orient = Qt.Orientation.Horizontal

        elif orientation == "vertical":
            orient = Qt.Orientation.Vertical

        super().setOrientation(orient)
