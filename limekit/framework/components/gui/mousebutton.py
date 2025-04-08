from PySide6.QtCore import Qt
from limekit.framework.core.engine.parts import EnginePart


# This class should not be used to directly set the mouse button, but rather to check which button was pressed.
class MouseButton(EnginePart):
    __button = Qt.MouseButton.LeftButton

    def __init__(self, button: Qt.MouseButton):
        self.__button = button

    def Left(self):
        return self.__button == Qt.MouseButton.LeftButton

    def Middle(self):
        return self.__button == Qt.MouseButton.MiddleButton

    def Right(self):
        return self.__button == Qt.MouseButton.RightButton
