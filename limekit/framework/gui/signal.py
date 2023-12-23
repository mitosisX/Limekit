from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtCore import QObject, Signal

"""

23 December, 2023 6:13 AM (Saturday)

The initial plan was to create a method that handles the emission
but then after consideration I thought to myself why one needs to use
a custom method when the variable holding the object already has a sensible name

local notifyThreadEnd = Signal()
notifyThreadEnd:setOnSignal(...)
notifyThreadEnd:emit()
"""


class QtSignal(QObject, EnginePart):
    """
    Signals are good when working with threads
    """

    name = "Signal"
    onSignalFunc = None
    qt_signal = Signal()

    def __init__(self):
        super().__init__()
        self.qt_signal.connect(self.__handleSignalEmit)

    def __handleSignalEmit(self):
        if self.onSignalFunc:
            self.onSignalFunc(self)

    def setOnSignal(self, onSignalFunc):
        self.onSignalFunc = onSignalFunc

    def relay(self):
        self.qt_signal.emit()
