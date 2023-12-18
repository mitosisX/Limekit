from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtWidgets import QStatusBar


class StatusBar(QStatusBar, EnginePart):
    def __init__(self):
        super().__init__(self, parent=None)
