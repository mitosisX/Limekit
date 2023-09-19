from PySide6.QtWidgets import QCheckBox
from limekit.framework.core.engine.parts import EnginePart


class CheckBox(EnginePart, QCheckBox):
    def __init__(self, text="CheckBox"):
        super().__init__()
        self.setText(text)

    def onStateChange(self, func):
        self.clicked.connect(lambda: func(self))

    def getText(self):
        return self.text()
