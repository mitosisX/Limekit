from PySide6.QtGui import QAction, QIcon
from limekit.framework.core.engine.parts import EnginePart

"""
Icon Size: 64x64

def setCheckable(bool)
"""


class ToolbarButton(QAction, EnginePart):
    onClickFunction = None

    def __init__(self, title=""):
        super().__init__(title)

        if title == "-":
            self.setSeparator(True)

        self.triggered.connect(self.__handleOnClick)

    def __handleOnClick(self):
        if self.onClickFunction:
            self.onClickFunction(self)

    def setText(slelf, text):
        super().setText(text)

    # Using setIcon complains about QIcon()
    def setIcon(self, image):
        super().setIcon(QIcon(image))

    def setOnClick(self, onClickFunction):
        self.onClickFunction = onClickFunction

    def setTooltip(self, text):
        self.setText(text)

    def isCheckable(self, checkable):
        super().isCheckable(checkable)

    def setChecked(self, checked):
        super().setChecked(checked)

    def setVisibility(self, visibility):
        self.setVisible(visibility)
