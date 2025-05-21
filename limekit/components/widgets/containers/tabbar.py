from PySide6.QtWidgets import QTabBar
from limekit.engine.parts import EnginePart


class TabBar(QTabBar):
    def __init__(self):
        super().__init__()
