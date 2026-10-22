from PySide6.QtWidgets import QFormLayout

from limekit.kernel.coerce import LuaIndex
from limekit.layouts.base import LimeLayout


class FormLayout(LimeLayout, QFormLayout):
    """Label/field pairs, one per row."""

    __lime__ = "ui.FormLayout"

    def __init__(self, parent=None):
        super().__init__(parent)

    def addChild(self, title, child=None):
        """`addChild("Name", field)` for a labelled row, `addChild(label,
        field)` for one whose label is a widget you made -- a ui.Label you
        can style, or reach later -- or `addChild(widget)` (title is
        actually the widget) for a full-width unlabelled one. Mirrors
        QFormLayout.addRow's own call shapes."""
        if isinstance(title, str):
            # A Limekit label, not the QLabel Qt would make from the text:
            # the row's title is then a widget like any other, and the
            # Inspector shows it by a name the author knows.
            from limekit.widgets.label import Label
            self.addRow(Label(title), child)
        elif child is not None:
            self.addRow(title, child)
        else:
            self.addRow(title)
        return self

    def addLayout(self, title, layout):
        from limekit.widgets.label import Label
        self.addRow(Label(str(title)), layout)
        return self

    def getRowAt(self, index):
        """1-indexed, like every other Limekit collection accessor."""
        item = self.itemAt(LuaIndex(index), QFormLayout.ItemRole.FieldRole)
        return item.widget() if item else None
