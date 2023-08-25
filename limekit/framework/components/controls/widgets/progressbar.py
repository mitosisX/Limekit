from PySide6.QtWidgets import QProgressBar
from limekit.framework.core.engine.parts import EnginePart


class ProgressBar(QProgressBar, EnginePart):
    def __init__(self):
        super().__init__()

    def setProgress(self, _value):
        self.setValue(_value)

    def getValue(self):
        return self.value()
