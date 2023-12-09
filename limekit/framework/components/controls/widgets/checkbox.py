from PySide6.QtWidgets import QCheckBox
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.components.base.base_widget import BaseWidget


class CheckBox(QCheckBox, BaseWidget, EnginePart):
    onStateChangedFunc = None

    def __init__(self, text=""):
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

    def setText(self, text):
        super().setText(text)

    def getText(self):
        return self.text()
