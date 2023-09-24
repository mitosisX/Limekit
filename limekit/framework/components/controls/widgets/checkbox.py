from PySide6.QtWidgets import QCheckBox
from limekit.framework.core.engine.parts import EnginePart


class CheckBox(QCheckBox, EnginePart):
    onStateChangedFunc = None

    def __init__(self, text=""):
        super().__init__()
        self.setText(text)
        self.clicked.connect(self._handleStateChange)

    def _handleStateChange(self, state):
        if self.onStateChangedFunc:
            self.onStateChangedFunc(self, state)

    def setOnChecked(self, onStateChangedFunc):
        self.onStateChangedFunc = onStateChangedFunc

    def getCheck(self):
        return self.isChecked()

    def setCheck(self, check):
        self.setChecked(check)

    def getText(self):
        return self.text()
