from PySide6.QtWidgets import QCheckBox

class CheckBox(QCheckBox):
    def __init__(self):
        super().__init__()
        self.setText("Checkbox")

    def onStateChange(self, func):
        self.clicked.connect(lambda:func(self))

    def getText(self):
        return self.text()
    