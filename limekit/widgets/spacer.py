"""Blank layout filler.

`QSpacerItem` is not a `QWidget` -- it has no `isEnabled`/`setVisible`/etc,
so it does not use the `LimeWidget` mixin, the same way `LimeAction` and
`LimeLayout` exist separately from it for their own non-widget Qt bases.
"""

from PySide6.QtWidgets import QSpacerItem

from limekit.kernel.declarative import LimeObject
from limekit.widgets.base import _to_int


class Spacer(LimeObject, QSpacerItem):
    __lime__ = "ui.Spacer"

    def __init__(self, width, height):
        super().__init__(_to_int(width, "width"), _to_int(height, "height"))
