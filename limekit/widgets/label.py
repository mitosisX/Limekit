from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel

from limekit.kernel.coerce import ALIGNMENTS, CURSORS, Enum
from limekit.kernel.spec import Prop
from limekit.widgets.base import LimeWidget

_alignment = Enum(ALIGNMENTS, "alignment")
_cursor = Enum(CURSORS, "cursor")


class Label(LimeWidget, QLabel):
    __lime__ = "ui.Label"

    text = Prop(str, default="", qt=("text", "setText"), coerce=str)
    wordWrap = Prop(bool, default=False, qt=("wordWrap", "setWordWrap"))
    textAlignment = Prop(object, qt=("alignment", "setAlignment"), coerce=_alignment)

    def __init__(self, text=""):
        super().__init__()
        self._image_path = ""
        self.setText(text)

    def setCursor(self, cursor):
        """Shared cursor map - the old one defined 'openhand' twice and
        mapped 'wait' to an arrow."""
        super().setCursor(_cursor(cursor))
        return self

    def setImage(self, path):
        self._image_path = path
        self.setPixmap(QPixmap(path))
        return self

    def getImagePath(self):
        return self._image_path
