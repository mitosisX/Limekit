from PySide6.QtWidgets import QPushButton

class Button(QPushButton):
    def __init__(self, text = "Button"):
        super().__init__()
        self.setText(text)

    def onClick(self, func):
        self.clicked.connect(lambda:func(self))

    def getText(self):
        return self.text()
    
    # Material properties (classes)
    # danger, warning, success
    def setMatProperty(self, class_):
        self.setProperty('class', class_)