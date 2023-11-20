from PySide6.QtWidgets import QGroupBox
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.components.base.base_widget import BaseWidget

"""
Only a layout can be used to add widgets using setLayout method
setCheckable(bool) displays a checkbox on the title bar

The following methods are used to make the widget checkeable or not, plus to check "checkeable" status
bool isCheckable() const
void setCheckable(bool checkable)
"""


class GroupBox(QGroupBox, BaseWidget, EnginePart):
    def __init__(self, title=""):
        super().__init__(title)
        BaseWidget.__init__(self, widget=self)

    def setLayout(self, layout):
        super().setLayout(layout)

    def setBackgroundColor(self, color):
        super().setStyleSheet(f"background-color: {color};")
