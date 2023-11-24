from PySide6.QtWidgets import QProgressBar

from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.components.base.base_widget import BaseWidget


class ProgressBar(QProgressBar, BaseWidget, EnginePart):
    def __init__(self):
        super().__init__()
        BaseWidget.__init__(self, widget=self)

    def setProgress(self, _value):
        self.setValue(_value)

    # Setting the range 0,0 makes the progress bar indeterminate
    def setRange(self, start, end):
        super().setRange(start, end)

    def setValue(self, value):
        super().setValue(value)

    def getValue(self):
        return self.value()
