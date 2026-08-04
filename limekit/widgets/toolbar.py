"""Toolbar and its QAction-based buttons.

`QToolBar` is a `QWidget` (`LimeWidget`); `ToolbarButton` wraps `QAction`,
a `QObject` rather than a `QWidget`, so it uses `LimeAction` like `MenuItem`.

1.x's `ToolbarButton.isChecked` called `super().isChecked()()` -- an extra,
erroneous pair of parentheses that would raise `TypeError: bool object is
not callable` the moment anyone called it. `LimeAction.checked` (a Prop)
replaces it with a working accessor.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QToolBar

from limekit.kernel.coerce import Enum, Size
from limekit.kernel.spec import Event, Prop
from limekit.widgets.action_base import LimeAction
from limekit.widgets.base import LimeWidget

_TOOLBUTTON_STYLES = {
    "icononly": Qt.ToolButtonStyle.ToolButtonIconOnly,
    "textonly": Qt.ToolButtonStyle.ToolButtonTextOnly,
    "textbesideicon": Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
    "textundericon": Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
    "followstyle": Qt.ToolButtonStyle.ToolButtonFollowStyle,
}
_toolbutton_style = Enum(_TOOLBUTTON_STYLES, "toolbar icon style")


class ToolbarButton(LimeAction, QAction):
    __lime__ = "ui.ToolbarButton"

    onClick = Event("triggered", passes_self=True)

    def __init__(self, text=""):
        super().__init__()
        if text:
            self.setText(str(text))

    def setMenu(self, menu):
        super().setMenu(menu)
        return self


class Toolbar(LimeWidget, QToolBar):
    __lime__ = "ui.Toolbar"

    movable = Prop(bool, qt=("isMovable", "setMovable"))
    floatable = Prop(bool, qt=("isFloatable", "setFloatable"))
    iconSize = Prop(object, qt=("iconSize", "setIconSize"), coerce=Size)
    toolButtonStyle = Prop(object, qt=("toolButtonStyle", "setToolButtonStyle"),
                            coerce=_toolbutton_style,
                            doc="how buttons show icon/text: icononly, "
                                "textonly, textbesideicon, textundericon, "
                                "followstyle")

    def __init__(self, title=""):
        super().__init__(str(title))

    def addButton(self, button):
        """Qt native (`addAction`) re-exposed so it chains."""
        self.addAction(button)
        return self

    def addChild(self, child):
        self.addWidget(child)
        return self

    def addSeparator(self):
        super().addSeparator()
        return self
