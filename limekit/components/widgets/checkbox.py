from PySide6.QtWidgets import QCheckBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from limekit.engine.parts import EnginePart
from limekit.engine.lifecycle.shutdown import destroy_engine
from limekit.components.base.widget_base import BaseWidget


class CheckBox(BaseWidget, QCheckBox, EnginePart):
    onStateChangedFunc = None

    def __init__(self, text=""):
        super().__init__()

        self.setText(text)
        self.clicked.connect(self._handleStateChange)

    def _handleStateChange(self, state):
        if self.onStateChangedFunc:
            try:
                self.onStateChangedFunc(self, state)
            except Exception as ex:
                print(ex)
                # destroy_engine()

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

    def setToolTip(self, tooltip):
        super().setToolTip(tooltip)

    def getToolTip(self):
        return self.toolTip()

    def setToolTipDuration(self, duration):
        self.toolTipDuration(duration)

    def setText(self, text):
        super().setText(text)

    def getText(self):
        return self.text()
