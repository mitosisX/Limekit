"""A dockable panel for QMainWindow's dock areas.

1.x's `setMagneticAreas` built a `Qt.DockWidgetArea` flag combination by
hand with a chain of `if area == "..."` string comparisons, silently
ignoring anything it didn't recognise instead of raising. `setAllowedAreas`
here reuses the shared `DOCK_AREAS` table (also used by `Window.addDockable`)
through the same `setContentAlignment`-style "combine one or more names"
pattern the layouts already use, so an unknown area name raises `BridgeError`
instead of being dropped on the floor.
"""

from PySide6.QtWidgets import QDockWidget, QWidget

from limekit.kernel.coerce import DOCK_AREAS, Enum, Icon
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import Event, Prop
from limekit.widgets.base import LimeWidget

_dock_area = Enum(DOCK_AREAS, "dock area")

_FEATURES = {
    "floatable": QDockWidget.DockWidgetFeature.DockWidgetFloatable,
    "movable": QDockWidget.DockWidgetFeature.DockWidgetMovable,
    "closable": QDockWidget.DockWidgetFeature.DockWidgetClosable,
}


class Dock(LimeWidget, QDockWidget):
    __lime__ = "ui.Dock"

    title = Prop(str, qt=("windowTitle", "setWindowTitle"), coerce=str)
    icon = Prop(object, qt=("windowIcon", "setWindowIcon"), coerce=Icon)
    floating = Prop(bool, qt=("isFloating", "setFloating"))

    onLocationChange = Event("dockLocationChanged", passes_self=True)
    onVisibilityChange = Event("visibilityChanged", passes_self=True)

    def __init__(self, title="Dockable"):
        super().__init__(str(title))
        self._central = QWidget()
        self.setWidget(self._central)

    # -- structure -----------------------------------------------------

    def setChild(self, child):
        self._central = child
        self.setWidget(child)
        return self

    def getChild(self):
        return self.widget()

    def setLayout(self, layout):
        self._central.setLayout(layout)
        return self

    def getLayout(self):
        return self._central.layout()

    def setTitleBarChild(self, child):
        self.setTitleBarWidget(child)
        return self

    def setAllowedAreas(self, *areas):
        """Combine one or more area names, e.g. ("left", "right")."""
        if not areas:
            raise BridgeError("setAllowedAreas needs at least one area")
        flags = _dock_area(areas[0])
        for name in areas[1:]:
            flags |= _dock_area(name)
        super().setAllowedAreas(flags)
        return self

    def setFeatures(self, *features):
        """Combine one or more of "floatable", "movable", "closable".

        Called with no arguments, the dock gets no features at all -- the
        same "none disables everything" behaviour 1.x's setProperties had,
        just without needing a Lua table wrapper to express it.
        """
        flags = QDockWidget.DockWidgetFeature.NoDockWidgetFeatures
        for name in features:
            try:
                flags |= _FEATURES[name]
            except KeyError:
                options = ", ".join(sorted(_FEATURES))
                raise BridgeError(
                    f"unknown dock feature {name!r}; expected one of: {options}"
                ) from None
        super().setFeatures(flags)
        return self
