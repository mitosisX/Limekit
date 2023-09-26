from PySide6.QtWidgets import QGroupBox
from limekit.framework.core.engine.parts import EnginePart

"""
Only a layout can be used to add widgets using setLayout method
setCheckable(bool) displays a checkbox on the title bar

The following methods are used to make the widget checkeable or not, plus to check "checkeable" status
bool isCheckable() const
void setCheckable(bool checkable)
"""


class GroupBox(QGroupBox, EnginePart):
    def __init__(self, title="GroupBox"):
        super().__init__(title)
