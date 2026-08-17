"""Command-link button (icon + title + description)."""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QCommandLinkButton

from limekit.kernel.coerce import Icon
from limekit.kernel.spec import Event, Prop
from limekit.widgets.base import LimeWidget, _to_int


class CommandButton(LimeWidget, QCommandLinkButton):
    __lime__ = "ui.CommandButton"

    text = Prop(str, qt=("text", "setText"), coerce=str)
    description = Prop(str, qt=("description", "setDescription"), coerce=str)
    icon = Prop(object, qt=("icon", "setIcon"), coerce=Icon)

    onClick = Event("clicked", passes_self=True, params=(("checked", "boolean"),))

    def __init__(self, text="Button"):
        super().__init__()
        self.setText(str(text))

    def setIconSize(self, width, height):
        super().setIconSize(QSize(_to_int(width, "width"), _to_int(height, "height")))
        return self
