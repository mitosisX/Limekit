from PySide6.QtWidgets import QRadioButton

class RadioButton(QRadioButton):
    def __init__(self):
        super().__init__()
        self.setText("Radiobutton")

    def onStateChange(self, func):
        self.clicked.connect(lambda:func(self))

    def getText(self):
        return self.text()
    