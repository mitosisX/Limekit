from PySide6.QtWidgets import QInputDialog

class InputDialog(object):
    def __init__(self, parent, title = "Title", text= "Dialog content"):
        self.dialog = QInputDialog.getText(parent, title, text)
        
    def getText(self):
        return str(self.dialog[0])