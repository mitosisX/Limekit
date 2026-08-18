from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import QLabel

from limekit.kernel.coerce import ALIGNMENTS, Alignment, CURSORS, Enum
from limekit.kernel.coerce import Colour
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import Prop, method
from limekit.widgets.base import LimeWidget

_alignment = Alignment
_cursor = Enum(CURSORS, "cursor")


class Label(LimeWidget, QLabel):
    __lime__ = "ui.Label"

    text = Prop(str, qt=("text", "setText"), coerce=str)
    wordWrap = Prop(bool, qt=("wordWrap", "setWordWrap"))
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

    @method({"width": "integer", "height": "integer"}, returns="self",
            doc="Scales the image. Call setImage first.")
    def setImageSize(self, width, height):
        """1.x also had `resizeImage`, a byte-for-byte duplicate of this;
        only one survives. See the migration guide."""
        pixmap = self.pixmap()
        if pixmap is None or pixmap.isNull():
            raise BridgeError(
                "setImageSize needs an image; call setImage(path) first"
            )
        from PySide6.QtCore import Qt
        self.setPixmap(pixmap.scaled(
            int(width), int(height),
            mode=Qt.TransformationMode.SmoothTransformation,
        ))
        return self

    # -- text appearance ---------------------------------------------------

    @method({"bold": "boolean"}, returns="self",
            doc="Draws the label's text bold, leaving the rest of the font alone.")
    def setBold(self, bold):
        font = self.font()
        font.setBold(bool(bold))
        QLabel.setFont(self, font)
        return self

    @method({"font": "string", "size": "integer"}, returns="self",
            doc="Sets the typeface, and optionally the point size.")
    def setFont(self, font, size=0):
        """Overrides QWidget.setFont so Lua can pass a family name.

        Hand-written rather than a Prop: the Prop collision guard would refuse
        to replace QWidget.setFont, and this takes two arguments anyway.
        """
        if isinstance(font, QFont):
            QLabel.setFont(self, font)
        else:
            QLabel.setFont(self, QFont(str(font), int(size)))
        return self

    @method({"size": "integer"}, returns="self", doc="The text size, in points.")
    def setTextSize(self, size):
        font = self.font()
        font.setPointSize(int(size))
        QLabel.setFont(self, font)
        return self

    @method({"colour": "string"}, returns="self", doc="The text colour.")
    def setTextColor(self, colour):
        self.setStyleSheet(f"color: {Colour(colour).name()};")
        return self
