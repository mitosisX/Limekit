from PySide6.QtCore import QThread, QThreadPool
from limekit.framework.core.engine.parts import EnginePart


class Worker(QThread, EnginePart):
    onThreadRun = None

    def setOnThreadRun(self, onThreadRun):
        self.onThreadRun = onThreadRun

    def run(self):
        if self.onThreadRun:
            self.onThreadRun()

    def sleep(self):
        self.sleep()

    def start(self):
        super().start()

    def stop(self):
        self.quit()

    def isRunning(self):
        return super().isRunning()
