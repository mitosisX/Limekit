from PySide6.QtWidgets import QWidget
from limekit.framework.core.engine.parts import EnginePart


class TabItem(QWidget, EnginePart):
    def __init__(self):
        pass

    def setLayout(self, child):
        super().setLayout(child)
