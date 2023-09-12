from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtCore import QRect, QPropertyAnimation, Qt


class Animation:
    animation_type = None
    animation = None

    def __init__(self, widget, anim=""):
        self.animation_type = anim
        self.animation = QPropertyAnimation(widget, b"geometry")
        self.animation.setDuration(10000)
        self.animation.setStartValue(QRect(0, 0, 100, 30))
        self.animation.setEndValue(QRect(250, 250, 100, 30))

    def start(self):
        self.animation.start()
