from PySide6.QtWidgets import QWidget

class TabItem:
    def __init__(self):
        self.widget = QWidget()
        
    def addChild(self, child):
        self.widget.setLayout(child)
        
    def offer(self):
        return self.widget