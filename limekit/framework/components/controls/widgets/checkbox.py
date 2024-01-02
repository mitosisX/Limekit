from PySide6.QtWidgets import QCheckBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.components.base.base_widget import BaseWidget


class CheckBox(QCheckBox, BaseWidget, EnginePart):
    onStateChangedFunc = None

    def __init__(self, text):
        super().__init__()
        BaseWidget.__init__(self, widget=self)

        self.setText(text)
        self.clicked.connect(self._handleStateChange)

    def _handleStateChange(self, state):
        if self.onStateChangedFunc:
            self.onStateChangedFunc(self, state)

    def setOnCheck(self, onStateChangedFunc):
        self.onStateChangedFunc = onStateChangedFunc

    def getCheck(self):
        return self.isChecked()

    def setCheck(self, check):
        self.setChecked(check)

    def setIcon(self, icon):
        super().setIcon(QIcon(icon))

    def setIconSize(self, width, height):
        super().setIconSize(QSize(width, height))

    def setTooltip(self, tooltip):
        self.setToolTip(tooltip)

    def getTooltip(self):
        return self.toolTip()

    def setTooltipDuration(self, duration):
        self.toolTipDuration(duration)

    def setText(self, text):
        super().setText(text)

    def getText(self):
        return self.text()
