from PySide6.QtWidgets import QTabBar
from limekit.framework.core.engine.parts import EnginePart


class TabBar(QTabBar, EnginePart):
    def __init__(self):
        super().__init__()
