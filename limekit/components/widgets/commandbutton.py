from PySide6.QtWidgets import QCommandLinkButton
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from limekit.engine.parts import EnginePart
from limekit.components.base.widget_base import BaseWidget


class CommandButton(BaseWidget, QCommandLinkButton, EnginePart):
    onClickFunc = None

    def __init__(self, text="Button"):
        super().__init__()

        self.setText(text)

        self.clicked.connect(self.__handleOnClick)

    def setOnClick(self, onClickFunc):
        self.onClickFunc = onClickFunc

    def __handleOnClick(self):
        if self.onClickFunc:
            self.onClickFunc(self)

    def getText(self):
        return self.text()

    def setText(self, text):
        super().setText(text)

    def setIcon(self, icon):
        super().setIcon(QIcon(icon))

    def setIconSize(self, width, height):
        super().setIconSize(QSize(width, height))

    def setDescription(self, description):
        super().setDescription(description)

    def getDescription(self):
        return self.description()
