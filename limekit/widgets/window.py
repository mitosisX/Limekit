"""The application window.

Closes four defects the 1.x `Window` carried:

- `onContextMenuEvent` was read in `contextMenuEvent` but never declared, so
  it raised `AttributeError` unless `setOnContextMenu` had been called first.
  Every handler slot is now initialised in `__init__`.
- `showEvent` called `center()` on *every* show, so re-showing a window that
  the user had moved yanked it back to the middle. The `just_shown` flag was
  declared for exactly this and never used; it is now honoured.
- `closeEvent` neither called `super()` nor accepted/ignored the event.
- `showEvent`/`resizeEvent` did not call `super()` either.

Window's events are Qt virtual-method overrides rather than signals, so they
cannot use the `Event` spec (which wraps `connect`). They are hand-written,
but every handler still crosses `guard()` -- there is no unguarded path.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QIcon, QPixmap
from PySide6.QtWidgets import QMainWindow, QWidget

from limekit.kernel.bridge.convert import as_mapping
from limekit.kernel.bridge.guard import guard
from limekit.kernel.coerce import DOCK_AREAS, TOOLBAR_AREAS, Enum, Icon
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import Prop, method
from limekit.widgets.base import LimeWidget, _to_int

_dock_area = Enum(DOCK_AREAS, "dock area")
_toolbar_area = Enum(TOOLBAR_AREAS, "toolbar area")

_EVENTS = (
    "onShown", "onClose", "onResize", "onMouseMove",
    "onMousePress", "onMouseRelease", "onMouseDoubleClick", "onContextMenu",
)


class Window(LimeWidget, QMainWindow):
    __lime__ = "ui.Window"

    title = Prop(str, qt=("windowTitle", "setWindowTitle"), coerce=str,
                 doc="the window's title-bar text")
    icon = Prop(object, qt=("windowIcon", "setWindowIcon"), coerce=Icon,
                doc="the window's icon")

    def __init__(self, options=None, **kwargs):
        """Accepts Lua's `Window{title=..., size={w, h}}` table-call sugar.

        `Window{...}` is just `Window({...})` -- a single positional table --
        so no `unpacks_lua_table` decorator is needed, and avoiding it keeps
        the constructor callable from Python with plain keywords, which the
        tests depend on.
        """
        super().__init__()
        options = as_mapping(options)
        options.update(kwargs)

        # Every handler slot exists from the start. The 1.x class declared
        # seven of the eight and read the missing one anyway.
        for name in _EVENTS:
            setattr(self, f"_{name}", None)

        self._just_shown = False
        self._central = QWidget()
        self.setCentralWidget(self._central)

        self.setTitle(options.get("title", "Limekit"))

        size = options.get("size")
        if size is not None:
            width, height = self._pair(size, "size")
            self.setSize(width, height)
        else:
            self.setSize(400, 400)

        location = options.get("location")
        if location is not None:
            x, y = self._pair(location, "location")
            self.setLocation(x, y)

        if options.get("icon") is not None:
            self.setIcon(options["icon"])

        self.setAnimated(True)

    @staticmethod
    def _pair(value, label):
        """Accept a Lua table {w, h} or any two-item Python sequence."""
        try:
            items = list(value.values()) if hasattr(value, "values") else list(value)
        except TypeError as exc:
            raise BridgeError(f"{label} must be a {{width, height}} pair") from exc
        if len(items) != 2:
            raise BridgeError(f"{label} needs exactly 2 values, got {len(items)}")
        return _to_int(items[0], f"{label}[1]"), _to_int(items[1], f"{label}[2]")

    # -- structure ---------------------------------------------------------

    def setLayout(self, layout):
        """QMainWindow cannot take a layout directly; it goes on the central widget."""
        self._central.setLayout(layout)
        return self

    def setMainChild(self, child):
        self.setCentralWidget(child)
        self._central = child
        return self

    @method({"name": "string"}, returns="any",
            doc="One of Qt's built-in icons, by name, e.g. \"SP_DirIcon\".")
    def getStandardIcon(self, name):
        from PySide6.QtWidgets import QStyle
        icon = getattr(QStyle.StandardPixmap, str(name), None)
        if icon is None:
            raise BridgeError(
                f"unknown standard icon {name!r}; getStandardIcons() lists "
                f"the valid names"
            )
        return self.style().standardIcon(icon)

    @method(returns="string[]", doc="Every standard icon name this platform offers.")
    def getStandardIcons(self):
        from PySide6.QtWidgets import QStyle
        from limekit.kernel.bridge.convert import outbound
        return outbound(sorted(
            n for n in dir(QStyle.StandardPixmap) if n.startswith("SP_")
        ))

    def center(self):
        from PySide6.QtWidgets import QApplication

        screen = QApplication.primaryScreen()
        if screen is None:                      # headless / no display
            return self
        frame = self.frameGeometry()
        frame.moveCenter(screen.availableGeometry().center())
        self.move(frame.topLeft())
        return self

    def maximize(self):
        self.showMaximized()
        return self

    def minimize(self):
        self.showMinimized()
        return self

    def setAlwaysOnTop(self, ontop=True):
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, bool(ontop))
        return self

    def setCustomCursor(self, cursor):
        self.setCursor(QCursor(QPixmap(cursor)))
        return self

    def addToolbar(self, toolbar, position="top"):
        self.addToolBar(_toolbar_area(position), toolbar)
        return self

    def addDockable(self, dock, area="left"):
        self.addDockWidget(_dock_area(area), dock)
        return self

    def setMenubar(self, menu):
        self.setMenuBar(menu)
        return self

    def getSize(self):
        size = self.size()
        return size.width(), size.height()

    # -- events ------------------------------------------------------------

    def _attach(self, name, handler):
        setattr(self, f"_{name}", guard(handler, widget="Window", event=name))
        return self

    def setOnShown(self, handler):
        return self._attach("onShown", handler)

    def setOnClose(self, handler):
        return self._attach("onClose", handler)

    def setOnResize(self, handler):
        return self._attach("onResize", handler)

    def setOnMouseMove(self, handler):
        return self._attach("onMouseMove", handler)

    def setOnMousePress(self, handler):
        return self._attach("onMousePress", handler)

    def setOnMouseRelease(self, handler):
        return self._attach("onMouseRelease", handler)

    def setOnMouseDoubleClick(self, handler):
        return self._attach("onMouseDoubleClick", handler)

    def setOnContextMenu(self, handler):
        return self._attach("onContextMenu", handler)

    # -- Qt overrides ------------------------------------------------------

    def showEvent(self, event):
        super().showEvent(event)
        if not self._just_shown:        # centre once, not on every show
            self._just_shown = True
            self.center()
        if self._onShown:
            self._onShown(self)

    def closeEvent(self, event):
        if self._onClose:
            self._onClose(self, event)
        if event.isAccepted():
            super().closeEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._onResize:
            width, height = event.size().width(), event.size().height()
            self._onResize(self, width, height)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self._onMouseMove:
            self._onMouseMove(self, event.pos().x(), event.pos().y())

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self._onMousePress:
            self._onMousePress(self, event.pos().x(), event.pos().y())

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self._onMouseRelease:
            self._onMouseRelease(self, event.pos().x(), event.pos().y())

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        if self._onMouseDoubleClick:
            self._onMouseDoubleClick(self, event.pos().x(), event.pos().y())

    def contextMenuEvent(self, event):
        if self._onContextMenu:
            self._onContextMenu(self, event.pos().x(), event.pos().y())
        else:
            super().contextMenuEvent(event)
