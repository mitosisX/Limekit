from PySide6.QtWidgets import QPushButton

from limekit.kernel.coerce import Icon
from limekit.kernel.spec import Event, Prop
from limekit.widgets.base import LimeWidget


class Button(LimeWidget, QPushButton):
    __lime__ = "ui.Button"

    text = Prop(str, qt=("text", "setText"), coerce=str,
                doc="the button's caption")
    icon = Prop(object, qt=("icon", "setIcon"), coerce=Icon)
    flat = Prop(bool, qt=("isFlat", "setFlat"))
    checkable = Prop(bool, qt=("isCheckable", "setCheckable"))
    checked = Prop(bool, qt=("isChecked", "setChecked"))

    onClick = Event("clicked", passes_self=True, doc="Fired when clicked.",
                     params=(("checked", "boolean"),))

    def __init__(self, text="Button"):
        super().__init__()
        self.setText(text)

    def click(self):
        """Qt native re-exposed so Lua's `button:click()` colon syntax works.

        lupa returns Python-defined methods unbound but Qt natives bound, so
        without this wrapper `b:click()` raises "takes no arguments (1 given)"
        while `b:getText()` is fine -- two calling conventions in one API.
        """
        super().click()
        return self

    def toggle(self):
        super().toggle()
        return self
