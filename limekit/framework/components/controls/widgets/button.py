from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from limekit.framework.core.engine.parts import EnginePart

from PySide6.QtWidgets import QSizePolicy


class Button(QPushButton, EnginePart):
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
            self.onClickFunc(self)

    def getText(self):
        return self.text()

    def setText(self, text):
        super().setText(text)

    def setResizeRule(self, horizontal: str, vertical: str):
        policies = {
            "fixed": QSizePolicy.Policy.Fixed,  # ignores all size changing
            "expanding": QSizePolicy.Policy.Expanding,  # makes sure to expand to all available spaces
            "ignore": QSizePolicy.Policy.Ignored,  # does nothing
        }

        horizontal = horizontal.lower()
        vertical = vertical.lower()

        if (horizontal in policies) and (vertical in policies):
            size_policy = QSizePolicy(policies.get(horizontal), policies.get(vertical))
            self.setSizePolicy(size_policy)

    # Material properties (classes)
    # danger, warning, success
    def setMatProperty(self, class_):
        self.setProperty("class", class_)

    # Also acts as the padding
    def setMargins(self, left, top, right, bottom):
        self.setContentsMargins(left, top, right, bottom)

    def setIcon(self, icon):
        super().setIcon(QIcon(icon))

    def setIconSize(self, width, height):
        super().setIconSize(QSize(width, height))

    # Makes the button loose all boarders and appear more like a Label until click
    def setFlat(self, flat):
        super().setFlat(flat)

    def setCheckable(self, checkable):
        super().setCheckable(checkable)

    def isChecked(self):
        return super().isChecked()

    def setClickAnimation(self):
        self.animateClick()
