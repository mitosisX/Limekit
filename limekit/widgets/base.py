"""Shared widget behaviour, declared once.

Replaces BaseWidget, whose pass-through overrides added nothing and which
half the widget set did not inherit from anyway.
"""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QSizePolicy

from limekit.kernel.coerce import SIZE_POLICIES, Enum
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import Prop, method

_size_policy = Enum(SIZE_POLICIES, "size policy")


def _to_int(value, label):
    """Coerce to int, translating a raw ValueError/TypeError into BridgeError.

    int("a") raises ValueError, int(None) raises TypeError -- neither is
    something a Lua caller should ever see; every bridge-boundary failure
    must surface as BridgeError.
    """
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise BridgeError(f"expected a number for {label}, got {value!r}") from exc


class LimeWidget(LimeObject):
    """Mixin for every QWidget subclass exposed to Lua."""

    enabled = Prop(bool, qt=("isEnabled", "setEnabled"))
    visible = Prop(bool, qt=("isVisible", "setVisible"))
    toolTip = Prop(str, qt=("toolTip", "setToolTip"), coerce=str)
    styleSheet = Prop(str, qt=("styleSheet", "setStyleSheet"), coerce=str)

    def setResizeRule(self, horizontal, vertical):
        """One definition, seven policies - not three in some widgets."""
        self.setSizePolicy(QSizePolicy(
            _size_policy(horizontal), _size_policy(vertical)
        ))
        return self

    def setSize(self, width, height):
        self.resize(_to_int(width, "width"), _to_int(height, "height"))
        return self

    def setFixedSize(self, width, height):
        super().setFixedSize(QSize(_to_int(width, "width"), _to_int(height, "height")))
        return self

    def setLocation(self, x, y):
        self.move(_to_int(x, "x"), _to_int(y, "y"))
        return self

    @method({"width": "integer"}, returns="self",
            doc="Resizes the width, leaving the height alone.")
    def setWidth(self, width):
        self.resize(_to_int(width, "width"), self.height())
        return self

    @method({"height": "integer"}, returns="self",
            doc="Resizes the height, leaving the width alone.")
    def setHeight(self, height):
        self.resize(self.width(), _to_int(height, "height"))
        return self

    @method({"left": "integer", "top": "integer", "right": "integer",
             "bottom": "integer"}, returns="self",
            doc="The space between the widget's edge and its contents.")
    def setMargins(self, left, top, right, bottom):
        self.setContentsMargins(
            _to_int(left, "left"), _to_int(top, "top"),
            _to_int(right, "right"), _to_int(bottom, "bottom"),
        )
        return self

    # -- size bounds -------------------------------------------------------
    #
    # 1.x carried these on individual widgets (widget_base, Window, Dockable,
    # ...), which is why porting Limer hit them immediately. Declared once
    # here instead: they apply to every QWidget, and `setSize`/`setFixedSize`
    # alone cannot express "at least this wide, but free to grow".

    @method({"width": "integer"}, returns="self",
            doc="The smallest width the widget may shrink to.")
    def setMinWidth(self, width):
        self.setMinimumWidth(_to_int(width, "width"))
        return self

    @method({"width": "integer"}, returns="self",
            doc="The largest width the widget may grow to.")
    def setMaxWidth(self, width):
        self.setMaximumWidth(_to_int(width, "width"))
        return self

    @method({"height": "integer"}, returns="self",
            doc="The smallest height the widget may shrink to.")
    def setMinHeight(self, height):
        self.setMinimumHeight(_to_int(height, "height"))
        return self

    @method({"height": "integer"}, returns="self",
            doc="The largest height the widget may grow to.")
    def setMaxHeight(self, height):
        self.setMaximumHeight(_to_int(height, "height"))
        return self

    @method({"width": "integer", "height": "integer"}, returns="self",
            doc="The smallest size the widget may shrink to.")
    def setMinSize(self, width, height):
        self.setMinimumSize(_to_int(width, "width"), _to_int(height, "height"))
        return self

    @method({"width": "integer", "height": "integer"}, returns="self",
            doc="The largest size the widget may grow to.")
    def setMaxSize(self, width, height):
        self.setMaximumSize(_to_int(width, "width"), _to_int(height, "height"))
        return self

    def setBackgroundColor(self, colour):
        self.setStyleSheet(f"background-color: {colour};")
        return self

    # -- Qt natives re-exposed as Python methods ---------------------------
    #
    # lupa hands back Python-defined functions *unbound* but Qt-native
    # methods *bound*. So `w:getText()` (generated, Python) works while
    # `w:show()` (Qt native) raises "takes no arguments (1 given)" -- the
    # user would have to remember which methods take `:` and which take `.`.
    #
    # Wrapping the natives people actually call keeps one rule for Lua:
    # always use `:`. 1.x achieved the same thing by hand-redeclaring these
    # on every widget class; doing it once on the shared base is the point
    # of having a shared base.

    def show(self):
        super().show()
        return self

    def hide(self):
        super().hide()
        return self

    def close(self):
        return super().close()

    def setFocus(self):
        super().setFocus()
        return self
