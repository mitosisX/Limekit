from PySide6.QtCore import QTimer

class Timer:
    def __init__(self, interval = 1000):
        self.timer = QTimer()
        self.setInterval(interval)
        # self.timer.start()
        
    def start(self):
        self.timer.start()
    
    def stop(self):
        self.timer.stop()
        
    def setInterval(self, interval):
        self.timer.setInterval(interval)
        
    def onTick(self, func):
        self.timer.timeout.connect(lambda: func(self))