from PySide6.QtCore import QTimer
from limekit.engine.parts import EnginePart


class Timer(QTimer, EnginePart):
    # name = "__timer"
    onTimeoutFunc = None

    def __init__(self, interval=None, onTimeoutFunc=None):
        super().__init__(parent=None)
        if interval is not None:
            self.setInterval(interval)
            self.start()
        self.timeout.connect(self.__handleTimeoutFunc)

    def __handleTimeoutFunc(self):
        if self.onTimeoutFunc:
            self.onTimeoutFunc(self)

    def start(self):
        super().start()

    def stop(self):
        super().stop()

    def setInterval(self, interval):
        super().setInterval(interval)

    def setOnTimeout(self, onTimeoutFunc):
        self.onTimeoutFunc = onTimeoutFunc

    @staticmethod
    def singleShot(msec, callback):
        """Execute callback once after msec milliseconds."""
        QTimer.singleShot(msec, callback)
