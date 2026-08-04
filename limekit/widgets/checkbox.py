from PySide6.QtWidgets import QCheckBox

from limekit.kernel.spec import Event, Prop
from limekit.widgets.base import LimeWidget


class CheckBox(LimeWidget, QCheckBox):
    __lime__ = "ui.CheckBox"

    text = Prop(str, default="", qt=("text", "setText"), coerce=str)
    checked = Prop(bool, default=False, qt=("isChecked", "setChecked"))

    onCheck = Event("clicked", passes_self=True)

    def __init__(self, text=""):
        super().__init__()
        self.setText(text)
