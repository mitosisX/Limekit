from PySide6.QtCore import Qt
from PySide6.QtWidgets import QProgressBar

from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.components.base.base_widget import BaseWidget


class ProgressBar(QProgressBar, BaseWidget, EnginePart):
    def __init__(self):
        super().__init__()
        BaseWidget.__init__(self, widget=self)

    # Setting the range 0,0 makes the progress bar indeterminate
    def setRange(self, start, end):
        super().setRange(start, end)

    def setValue(self, value):
        super().setValue(value)

    def getValue(self):
        return self.value()

    def setOrientation(self, orientation):
        orientation = orientation.lower()

        if orientation == "horizontal":
            orient = Qt.Orientation.Horizontal

        elif orientation == "vertical":
            orient = Qt.Orientation.Vertical

        super().setOrientation(orient)
