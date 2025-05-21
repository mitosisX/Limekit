from PySide6.QtWidgets import QRadioButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from limekit.engine.parts import EnginePart


class RadioButton(QRadioButton, EnginePart):
    onClickFunc = None

    def __init__(self, text=""):
        super().__init__(text, parent=None)

        self.clicked.connect(self.__handleOnClick)

        self.setText(text)

    def setOnClick(self, onClickFunc):
        self.onClickFunc = onClickFunc

    def __handleOnClick(self, state):
        if self.onClickFunc:
            self.onClickFunc(self, state)

    def setToolTip(self, tooltip):
        super().setToolTip(tooltip)

    def getToolTip(self):
        return self.toolTip()

    def setToolTipDuration(self, duration):
        self.toolTipDuration(duration)

    def setText(self, text):
        super().setText(text)

    def getText(self):
        return self.text()

    def setIcon(self, icon):
        super().setIcon(QIcon(icon))

    def setIconSize(self, width, height):
        super().setIconSize(QSize(width, height))
