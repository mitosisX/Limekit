from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from limekit.framework.core.engine.parts import EnginePart


class Button(EnginePart, QPushButton):
    onClickFunc = None

    def __init__(self, text="Button"):
        super().__init__()
        self.setText(text)

        self.clicked.connect(self.__handleOnClick)

    def setOnClick(self, onClickFunc):
        self.onClickFunc = onClickFunc
        # mouse_event = QApplication.mouseButtons()

        # if mouse_event == Qt.LeftButton:
        #     print("Left button clicked")
        # elif mouse_event == Qt.RightButton:
        #     print("Right button clicked")

        # double_click = QApplication.mouseDoubleClickInterval()
        # if self.button.underMouse() and self.button.clickCount() == 2:
        #     print("Double click")

    def __handleOnClick(self):
        if self.onClickFunc:
            try:
                self.onClickFunc(self)
            except Exception as ex:
                print(ex)

    def getText(self):
        return self.text()

    # Material properties (classes)
    # danger, warning, success
    def setMatProperty(self, class_):
        self.setProperty("class", class_)
