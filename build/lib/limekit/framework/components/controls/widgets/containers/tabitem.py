from PySide6.QtWidgets import QWidget
from limekit.framework.core.engine.parts import EnginePart


class TabItem(EnginePart):
    def __init__(self):
        self.widget = QWidget()

    def addChild(self, child):
        self.widget.setLayout(child)

    def offer(self):
        return self.widget
