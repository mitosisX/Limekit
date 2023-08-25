from PySide6.QtWidgets import QCheckBox
from limekit.framework.core.engine.parts import EnginePart


class CheckBox(EnginePart, QCheckBox):
    def __init__(self):
        super().__init__()

    def onStateChange(self, func):
        self.clicked.connect(lambda: func(self))

    def getText(self):
        return self.text()
