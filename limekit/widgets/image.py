"""A QLabel that displays a scaled pixmap.

1.x defined `resizeImage` and `setImageSize` as byte-for-byte identical
methods; only `setImageSize` survives here.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel

from limekit.kernel.bridge.guard import guard
from limekit.kernel.coerce import ALIGNMENTS, Alignment, Enum
from limekit.kernel.errors import BridgeError
from limekit.widgets.base import LimeWidget, _to_int

_alignment = Alignment


class Image(LimeWidget, QLabel):
    __lime__ = "ui.Image"

    def __init__(self, path=""):
        super().__init__()
        self._path = ""
        self._pixmap = None
        self._onClick = None
        if path:
            self.setImage(path)

    def setImage(self, path):
        self._path = path
        self._pixmap = QPixmap(path)
        self.setPixmap(self._pixmap)
        return self

    def getImagePath(self):
        return self._path

    def setImageSize(self, width, height):
        if self._pixmap is None:
            raise BridgeError("Image has no source; call setImage first")
        scaled = self._pixmap.scaled(
            _to_int(width, "width"), _to_int(height, "height"),
            mode=Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(scaled)
        return self

    def setImageAlignment(self, *alignments):
        if not alignments:
            raise BridgeError("setImageAlignment needs at least one alignment")
        flags = _alignment(alignments[0])
        for name in alignments[1:]:
            flags |= _alignment(name)
        self.setAlignment(flags)
        return self

    def setOnClick(self, handler):
        self._onClick = guard(handler, widget="Image", event="onClick")
        return self

    def mousePressEvent(self, event):
        if self._onClick:
            self._onClick(self)
        super().mousePressEvent(event)
