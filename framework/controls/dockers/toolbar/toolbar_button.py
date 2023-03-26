from PySide6.QtGui import QAction, QIcon

"""
Icon Size: 64x64

def setCheckable(bool)
"""

class ToolbarButton(QAction):
    def __init__(self):
        super().__init__()
        
    # Using setIcon complains about QIcon()
    def setImage(self, image):
        self.setIcon(QIcon(image))
        
    def onClick(self, func):
        self.triggered.connect(lambda:func(self))
        
    def setTooltip(self, text):
        self.setText(text)