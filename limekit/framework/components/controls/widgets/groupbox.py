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

    def setStyle(self, styleSheet):
        self.setStyleSheet(styleSheet)

    def setBackgroundColor(self, color):
        super().setStyleSheet(f"background-color: {color};")

    def setTitle(self, title):
        super().setTitle(title)

    def getTitle(self):
        return self.title()

    def setToolTip(self, tooltip):
        super().setToolTip(tooltip)

    def setCheckable(self, checkable):
        super().setCheckable(checkable)

    def getCheck(self):
        return self.isChecked()

    def setChecked(self, checked):
        super().setChecked(checked)

    def setFlat(self, flat):
        super().setFlat(flat)

    def getToolTip(self):
        return self.toolTip()

    def setToolTipDuration(self, duration):
        super().toolTipDuration(duration)
