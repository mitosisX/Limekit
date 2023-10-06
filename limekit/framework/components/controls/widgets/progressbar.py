from PySide6.QtWidgets import QProgressBar
from limekit.framework.core.engine.parts import EnginePart


class ProgressBar(QProgressBar, EnginePart):
    def __init__(self):
        super().__init__()

    def setProgress(self, _value):
        self.setValue(_value)

    def setRange(self, start, end):
        super().setRange(start, end)

    def setValue(self, value):
        super().setValue(value)

    def getValue(self):
        return self.value()
