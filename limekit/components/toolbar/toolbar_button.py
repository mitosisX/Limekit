from PySide6.QtGui import QAction, QIcon
from limekit.engine.parts import EnginePart
from limekit.engine.lifecycle.shutdown import destroy_engine

"""
Icon Size: 64x64

def setCheckable(bool)
"""


class ToolbarButton(QAction, EnginePart):
    onClickFunction = None

    def __init__(self, title=""):
        super().__init__(text=title if title != "-" else "", parent=None)

        if title == "-":
            self.setSeparator(True)

        self.triggered.connect(self.__handleOnClick)

    def __handleOnClick(self):
        if self.onClickFunction:
            try:
                self.onClickFunction(self)
            except Exception as ex:
                print(ex)
                # destroy_engine()

    def setText(slelf, text):
        super().setText(text)

    def setEnabled(self, enabled):
        super().setEnabled(enabled)

    # Using setIcon complains about QIcon()
    def setIcon(self, image):
        super().setIcon(QIcon(image))

    def setOnClick(self, onClickFunction):
        self.onClickFunction = onClickFunction

    def setToolTip(self, text):
        super().setToolTip(text)

    def setMenu(self, menu):
        super().setMenu(menu)

    def setCheckable(self, checkable):
        super().setCheckable(checkable)

    # Automatically checks it when setCheckable is true
    def toggleCheck(self):
        self.toggle()

    def isChecked(self):
        return super().isChecked()()

    def setChecked(self, checked):
        super().setChecked(checked)

    def setVisibility(self, visibility):
        self.setVisible(visibility)

    def setShortcut(self, shortcut):
        super().setShortcut(shortcut)

    def setStatusTip(self, text):
        super().setStatusTip(text)
