from PySide6.QtWidgets import QStatusBar

from limekit.kernel.spec import Prop
from limekit.widgets.base import LimeWidget, _to_int


class StatusBar(LimeWidget, QStatusBar):
    __lime__ = "ui.StatusBar"

    sizeGripEnabled = Prop(bool, qt=("isSizeGripEnabled", "setSizeGripEnabled"))

    def setText(self, text, timeout=0):
        """1.x's `setText` was really `showMessage`; named to match how
        every other Limekit widget exposes its caption."""
        self.showMessage(str(text), _to_int(timeout, "timeout"))
        return self

    def clear(self):
        self.clearMessage()
        return self

    def addChild(self, child, stretch=0):
        self.addWidget(child, _to_int(stretch, "stretch"))
        return self

    def addPermanentChild(self, child, stretch=0):
        self.addPermanentWidget(child, _to_int(stretch, "stretch"))
        return self
