from PySide6.QtWidgets import QButtonGroup
from limekit.framework.core.engine.parts import EnginePart

"""
Only a layout can be used to add widgets using setLayout method
setCheckable(bool) displays a checkbox on the title bar

The following methods are used to make the widget checkeable or not, plus to check "checkeable" status
bool isCheckable() const
void setCheckable(bool checkable)
"""


class ButtonGroup(QButtonGroup, EnginePart):
    # NOTE: Doesnt have to e added to any layout
    onClickFunc = None

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.buttonClicked.connect(self.__handleOnClick)

    def addChild(self, *buttons):
        for button in buttons:
            self.addButton(button)

    def setOnClick(self, onClickFunc):
        self.onClickFunc = onClickFunc

    def __handleOnClick(self, button):
        if self.onClickFunc:
            self.onClickFunc(self, button)
