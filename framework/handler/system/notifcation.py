from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QSystemTrayIcon

# Remember to call show() for display
        
class Notification(QSystemTrayIcon):
    def __init__(self):
        super().__init__()
    
    def onShown(self, func):
        self.clicked.activated(lambda:func(self))
    
    def onClick(self, func):
        self.clicked.messageClicked(lambda:func(self))
        
    def setMessage(self, _title, _message, _icon, _duration):
        icon = QIcon(_icon)
        
        self._tray_icon.showMessage(
                _title,
                _message,
                icon,
                _duration,
            )