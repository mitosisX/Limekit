from PySide6.QtCore import QPoint
from limekit.framework.core.engine.parts import EnginePart


# This class should not be used to directly set the mouse button, but rather to check which button was pressed.
class MousePosition(EnginePart):
    __x = 0
    __y = 0

    def __init__(self, pos: QPoint):
        self.__x = pos.x()
        self.__y = pos.y()

    def X(self):
        return self.__x

    def Y(self):
        return self.__y
