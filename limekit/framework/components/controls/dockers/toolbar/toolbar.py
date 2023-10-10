from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QToolBar
from PySide6.QtGui import QFont
from limekit.framework.core.engine.parts import EnginePart

"""
Icon Size: 64x64

def addSeparator()
"""


class Toolbar(QToolBar, EnginePart):
    def __init__(self, name="my toolbar"):
        super().__init__()
        self.setIconSize(QSize(30, 30))
        font = QFont()
        font.setPointSize(8)  # Set the font size to 16 points

        self.setFont(font)

    """
    Determines how buttons are displayed on the toolbar
    """

    def setImageStyle(self, _status):
        button_style = Qt.ToolButtonStyle.ToolButtonFollowStyle
        status = _status.lower()

        if status == "icononly":
            button_style = Qt.ToolButtonStyle.ToolButtonIconOnly

        elif status == "textonly":
            button_style = Qt.ToolButtonStyle.ToolButtonTextOnly

        elif status == "textbesideicon":
            button_style = Qt.ToolButtonStyle.ToolButtonTextBesideIcon

        elif status == "textundericon":
            button_style = Qt.ToolButtonStyle.ToolButtonTextUnderIcon

        elif status == "followstyle":
            button_style = Qt.ToolButtonStyle.ToolButtonFollowStyle

        self.setToolButtonStyle(button_style)

    def addButton(self, button):
        self.addAction(button)
