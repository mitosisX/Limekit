from PySide6.QtWidgets import QRadioButton

from limekit.kernel.coerce import Icon, Size
from limekit.kernel.spec import Event, Prop
from limekit.widgets.base import LimeWidget


class RadioButton(LimeWidget, QRadioButton):
    __lime__ = "ui.RadioButton"

    text = Prop(str, qt=("text", "setText"), coerce=str)
    checked = Prop(bool, qt=("isChecked", "setChecked"))
    icon = Prop(object, qt=("icon", "setIcon"), coerce=Icon)
    iconSize = Prop(object, qt=("iconSize", "setIconSize"), coerce=Size,
                     doc="a {width, height} pair")

    onClick = Event("clicked", passes_self=True)

    def __init__(self, text=""):
        super().__init__()
        self.setText(text)
