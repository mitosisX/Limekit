from PySide6.QtWidgets import QGroupBox

from limekit.kernel.spec import Prop
from limekit.widgets.base import LimeWidget


class GroupBox(LimeWidget, QGroupBox):
    __lime__ = "ui.GroupBox"

    title = Prop(str, qt=("title", "setTitle"), coerce=str)
    checkable = Prop(bool, qt=("isCheckable", "setCheckable"))
    checked = Prop(bool, qt=("isChecked", "setChecked"))
    flat = Prop(bool, qt=("isFlat", "setFlat"))
    layout = Prop(object, qt=("layout", "setLayout"))

    def __init__(self, title=""):
        super().__init__()
        self.setTitle(title)
