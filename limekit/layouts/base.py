"""Shared layout behaviour.

`QLayout` is not a `QWidget`, so `LimeWidget`'s props (`enabled`, `visible`,
`toolTip`, `styleSheet`) do not apply to it. Layouts get their own small base
rather than inheriting four accessors that would silently fail to install.

Both classes here are abstract mixins: they declare props whose Qt methods
live on the concrete `QLayout` subclass, so accessor installation is deferred
until a concrete layout combines them with a real Qt base.
"""

from PySide6.QtWidgets import QLayout

from limekit.kernel.coerce import ALIGNMENTS, Enum, LuaIndex
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import Prop

_alignment = Enum(ALIGNMENTS, "alignment")


def _to_int(value, label):
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise BridgeError(f"expected a number for {label}, got {value!r}") from exc


class LimeLayout(LimeObject):
    """Mixin for every QLayout subclass exposed to Lua."""

    spacing = Prop(int, qt=("spacing", "setSpacing"))

    def setMargins(self, left, top, right, bottom):
        """Also acts as the layout's padding."""
        self.setContentsMargins(
            _to_int(left, "left"), _to_int(top, "top"),
            _to_int(right, "right"), _to_int(bottom, "bottom"),
        )
        return self

    def getCount(self):
        return self.count()

    def getChildAt(self, index):
        """1-indexed, like every Limekit collection accessor."""
        item = self.itemAt(LuaIndex(index))
        return item.widget() if item else None

    def getLayoutAt(self, index):
        item = self.itemAt(LuaIndex(index))
        return item.layout() if item else None

    def setContentAlignment(self, *alignments):
        """Combine one or more alignment names, e.g. ("center", "top")."""
        if not alignments:
            raise BridgeError("setContentAlignment needs at least one alignment")
        flags = _alignment(alignments[0])
        for name in alignments[1:]:
            flags |= _alignment(name)
        self.setAlignment(flags)
        return self

    def clear(self):
        """Remove and delete every item in the layout."""
        while self.count():
            item = self.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        return self


class BoxLayout(LimeLayout):
    """Shared behaviour for the linear layouts (VLayout, HLayout).

    GridLayout deliberately does not inherit this: its `addChild` takes a
    row and column, so sharing the signature would be a lie.
    """

    def addChild(self, child, stretch=0):
        self.addWidget(child, _to_int(stretch, "stretch"))
        return self

    def addLayout(self, layout, stretch=0):
        super().addLayout(layout, _to_int(stretch, "stretch"))
        return self

    def addStretch(self, stretch=1):
        super().addStretch(_to_int(stretch, "stretch"))
        return self

    def addSpacing(self, size):
        super().addSpacing(_to_int(size, "size"))
        return self

    def addSpacer(self, spacer):
        """Adds a `ui.Spacer`.

        A QSpacerItem is not a QWidget, so `addChild` cannot take one -- it
        calls addWidget and Qt rejects it. 1.x had this method; 2.0 dropped
        it, which left `ui.Spacer` registered but impossible to place.
        """
        self.addSpacerItem(spacer)
        return self
