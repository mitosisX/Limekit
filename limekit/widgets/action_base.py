"""Shared behaviour for QAction-based Lua objects.

`QAction` is a `QObject`, not a `QWidget` -- `LimeWidget`'s props
(`enabled`, `visible`, `toolTip`, `styleSheet`) happen to all exist on
`QAction` too by coincidence of naming, but relying on that would be an
accident, not a design; `QAction` has no `styleSheet`. `MenuItem` and
`ToolbarButton` get their own small mixin instead, the same way `LimeLayout`
exists separately from `LimeWidget` for `QLayout`.
"""

from limekit.kernel.coerce import Icon
from limekit.kernel.declarative import LimeObject
from limekit.kernel.spec import Prop


class LimeAction(LimeObject):
    """Mixin for every QAction subclass exposed to Lua."""

    text = Prop(str, qt=("text", "setText"), coerce=str,
                doc="the action's caption")
    icon = Prop(object, qt=("icon", "setIcon"), coerce=Icon)
    enabled = Prop(bool, qt=("isEnabled", "setEnabled"))
    visible = Prop(bool, qt=("isVisible", "setVisible"))
    checkable = Prop(bool, qt=("isCheckable", "setCheckable"))
    checked = Prop(bool, qt=("isChecked", "setChecked"))
    separator = Prop(bool, qt=("isSeparator", "setSeparator"))
    toolTip = Prop(str, qt=("toolTip", "setToolTip"), coerce=str)
    statusTip = Prop(str, qt=("statusTip", "setStatusTip"), coerce=str)
    # QAction.setShortcut accepts a plain string directly (PySide converts
    # it to QKeySequence), so a plain str coercion is enough here.
    shortcut = Prop(str, qt=("shortcut", "setShortcut"), coerce=str)

    def toggle(self):
        """Qt native re-exposed so Lua's `item:toggle()` colon syntax works."""
        super().toggle()
        return self

    def trigger(self):
        super().trigger()
        return self
