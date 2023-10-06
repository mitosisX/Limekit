from PySide6.QtWidgets import QRadioButton
from limekit.framework.core.engine.parts import EnginePart


class RadioButton(QRadioButton, EnginePart):
    def __init__(self, text="RadioButton"):
        super().__init__(text, parent=None)

        self.setText("Radiobutton")

    def onStateChange(self, func):
        self.clicked.connect(lambda: func(self))

    def getText(self):
        return self.text()
