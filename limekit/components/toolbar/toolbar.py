from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QToolBar
from PySide6.QtGui import QFont
from limekit.engine.parts import EnginePart

"""
Icon Size: 64x64

def addSeparator()
"""


class Toolbar(QToolBar, EnginePart):
    def __init__(self, title=""):
        super().__init__(title)
        # self.setIconSize(30, 30)
        font = QFont()
        font.setPointSize(8)  # Set the font size to 16 points

        self.setFont(font)

    def setIconSize(self, width, height):
        super().setIconSize(QSize(width, height))

    """
    Determines how buttons are displayed on the toolbar
    """

    def setIconStyle(self, status):
        button_style = Qt.ToolButtonStyle.ToolButtonFollowStyle
        status = status.lower()

        if status == "icononly":
            # Icon only, no text
            button_style = Qt.ToolButtonStyle.ToolButtonIconOnly

        elif status == "textonly":
            # Text only, no icon
            button_style = Qt.ToolButtonStyle.ToolButtonTextOnly

        elif status == "textbesideicon":
            # Icon and text, with text beside the icon
            button_style = Qt.ToolButtonStyle.ToolButtonTextBesideIcon

        elif status == "textundericon":
            # Icon and text, with text under the icon
            button_style = Qt.ToolButtonStyle.ToolButtonTextUnderIcon

        elif status == "followstyle":
            # Follow the host desktop style, with text under the icon, meaning that
            # your application will default to following the standard/global setting
            # for the desktop on which the application runs. This is generally
            # recommended to make your application feel as native as possible.

            button_style = Qt.ToolButtonStyle.ToolButtonFollowStyle

        self.setToolButtonStyle(button_style)

    def addButton(self, button):
        self.addAction(button)

    def addSeparator(self):
        super().addSeparator()

    def addChild(self, child):
        self.addWidget(child)
