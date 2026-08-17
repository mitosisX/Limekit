"""Groups CheckBoxes/RadioButtons for mutual exclusion or joint handling.

QButtonGroup is a QObject, not a QWidget - it is never added to a layout, so
it uses `LimeObject` directly rather than the `LimeWidget` mixin (whose props
wrap QWidget methods QButtonGroup does not have).
"""

from PySide6.QtWidgets import QButtonGroup

from limekit.kernel.declarative import LimeObject
from limekit.kernel.spec import Event, Prop


class ButtonGroup(LimeObject, QButtonGroup):
    __lime__ = "ui.ButtonGroup"

    exclusive = Prop(bool, qt=("exclusive", "setExclusive"))

    onClick = Event("buttonClicked", passes_self=True,
                     params=(("button", "any"),))

    def addButton(self, button):
        """Qt native re-exposed so Lua's `group:addButton(b)` colon syntax works."""
        super().addButton(button)
        return self

    def removeButton(self, button):
        super().removeButton(button)
        return self
