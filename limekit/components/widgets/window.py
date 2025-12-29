import lupa

from PySide6.QtCore import Qt, QEvent
from PySide6.QtWidgets import QMainWindow, QWidget, QStyle
from PySide6.QtGui import QIcon, QCursor, QPixmap

from limekit.engine.lifecycle.app import App
from limekit.engine.parts import EnginePart
from limekit.gui.mousebutton import MouseButton
from limekit.gui.mouse_position import MousePosition
from limekit.components.dockable.dockable_widget import Dock
from limekit.utils.converters import Converter


class Window(QMainWindow, EnginePart):
    just_shown = False  # To be used for any first launch logic: center()...
    onShownEvent = None
    onResizeEvent = None
    onCloseEvent = None
    onResizeEvent = None
    onMouseMoveEvent = None
    onMousePressEvent = None
    onMouseReleaseEvent = None
    onMouseDoubleClickEvent = None

    @lupa.unpacks_lua_table
    def __init__(self, kwargs={}):
        super().__init__()

        (
            self.setTitle(kwargs["title"])
            if "title" in kwargs
            else self.setTitle("Limekit - lua framework")
        )

        if "size" in kwargs:
            try:
                width, height = kwargs["size"].values()
                self.setSize(width, height)
            except ValueError as ex:
                from limekit.core.error_handler import warn
                warn(f"Invalid window size format, using default 400x400: {ex}", "Window")
                self.setSize(400, 400)
        else:
            self.setSize(400, 400)

        # if "fixedSize" in kwargs:
        #     try:
        #         width, height = kwargs["fixedSize"].values()
        #         self.setFixedSize(width, height)
        #     except ValueError as ex:
        #         self.setFixedSize(400, 400)

        # else:
        #     self.setFixedSize(400, 400)

        if "location" in kwargs:
            location = kwargs["location"]
            pos = len(location)

            if pos == 2:
                x, y = location.values()

                self.setLocation(x, y)
        else:
            self.center()

        self.setIcon(kwargs["icon"]) if "icon" in kwargs else None

        # if "icon" in kwargs:
        #     self.setIcon(kwargs["icon"])
        # else:
        #     # set default icon
        #     pass

        self.widget = QWidget()

        self.setCentralWidget(self.widget)

        self.setAnimated(True)

    def maximize(self):
        self.showMaximized()

    def eventFilter(self, obj, e: QEvent):
        if obj is self.parent():
            if e.type() == QEvent.Resize:
                self.resize(e.size())
            elif e.type() == QEvent.ChildAdded:
                self.raise_()

        return super().eventFilter(obj, e)

    def setMaxHeight(self, height):
        self.setMaximumHeight(height)

    def setMinHeight(self, height):
        self.setMinimumHeight(height)

    def setMaxWidth(self, width):
        self.setMaximumWidth(width)

    def setMinWidth(self, width):
        self.setMinimumWidth(width)

    def setMaxSize(self, width, height):
        self.setMaximumSize(width, height)

    def minimize(self):
        self.showMinimized()

    """
    This method only overrides the cursor for the MainWindow due to the fact that overriding the whole
    QApplication renders the control box uninteractive or unresponsive.
    """

    def setCustomCursor(self, cursor):
        cursor_image = QPixmap(cursor)  # Replace with the actual file path

        # Create a custom cursor using the QPixmap
        custom_cursor = QCursor(cursor_image)

        # Set the custom cursor for the main window
        self.setCursor(custom_cursor)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setMainChild(self, child: QWidget):
        self.setCentralWidget(None)  # remove everything first
        self.setCentralWidget(child)

    def setSize(self, width, height):
        self.resize(width, height)

    def setMinSize(self, width, height):
        self.setMinimumSize(width, height)

    def setLocation(self, x, y):
        self.move(x, y)

    def setLayout(self, layout):
        self.widget.setLayout(layout)
        # self.layout.addLayout(layout)

    def addDockable(self, dock, area):
        self.addDockWidget(self.__setDockArea(area), dock)

    def __setDockArea(self, area):
        """Sets the Qt.DockWidgetArea value corresponding to a string representation of a dock area.

        Args:
            dock_area: A string representing the dock area. Valid values are:
                - "left"
                - "right"
                - "top"
                - "bottom"

        Returns:
            The Qt.DockWidgetArea value corresponding to the string input.
        """

        selected_area = area.lower()

        if selected_area == "left":
            return Qt.DockWidgetArea.LeftDockWidgetArea

        elif selected_area == "right":
            return Qt.DockWidgetArea.RightDockWidgetArea

        elif selected_area == "top":
            return Qt.DockWidgetArea.TopDockWidgetArea

        elif selected_area == "bottom":
            return Qt.DockWidgetArea.BottomDockWidgetArea

        elif selected_area == "allareas":
            return Qt.DockWidgetArea.AllDockWidgetAreas

        else:
            return Qt.DockWidgetArea.NoDockWidgetArea

    def setIcon(self, icon):
        self.setWindowIcon(QIcon(icon))

    def addToolbar(self, toolbar, position="top"):
        positions = {
            "left": Qt.ToolBarArea.LeftToolBarArea,
            "top": Qt.ToolBarArea.TopToolBarArea,
            "right": Qt.ToolBarArea.RightToolBarArea,
            "bottom": Qt.ToolBarArea.BottomToolBarArea,
        }

        super().addToolBar(
            positions[position] if positions.get(position) else positions["top"],
            toolbar,
        )

    # Unnecessary, yeah! I know! I just disliked having to CamelCase to the end ;-).. I know it doesn't make sense
    def setMenubar(self, menu):
        self.setMenuBar(menu)

    """
    The Dock can accept parent in it's constructor, and using this makes the dock
    take up the whole are as this essentially makes the "central widget" of its parent
    
    While in this case, this method allows individual Docks to be added to the Window
    """

    def center(self):
        qr = self.frameGeometry()
        cp = App.app.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def setFixedSize(self, width, height):
        super().setFixedSize(width, height)

    def getSize(self):
        return self.size().width(), self.size().height()

    def setAlwaysOnTop(self, ontop: bool):
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

    # Events ----------------------
    def setOnShown(self, func):
        self.onShownEvent = func

    def showEvent(self, event):
        self.center()

        super().showEvent(event)
        if self.onShownEvent:
            self.onShownEvent(self)

    def setOnClose(self, func):
        self.onCloseEvent = func

    # event has: ignore and accept
    def closeEvent(self, event):
        if self.onCloseEvent:
            self.onCloseEvent(self, event)

    def setOnResize(self, func):
        self.onResizeEvent = func

    def resizeEvent(self, event):
        if self.onResizeEvent:
            self.onResizeEvent(self)

    def setOnMouseMove(self, func):
        self.onMouseMoveEvent = func

    def mouseMoveEvent(self, event):
        if self.onMouseMoveEvent:
            mp = MousePosition(event.pos())  # mp: mouse position

            self.onMouseMoveEvent(self, mp)

    def setOnMousePress(self, func):
        self.onMousePressEvent = func

    def mousePressEvent(self, event):
        if self.onMousePressEvent:
            mb = MouseButton(event.button())  # mb: mouse button

            self.onMousePressEvent(self, mb)

    def setOnMouseRelease(self, func):
        self.onMouseReleaseEvent = func

    def mouseReleaseEvent(self, event):
        if self.onMouseReleaseEvent:
            mb = MouseButton(event.button())  # mb: mouse button

            self.onMouseReleaseEvent(self, mb)

    def setOnMouseDoubleClick(self, func):
        self.onMouseDoubleClickEvent = func

    def mouseDoubleClickEvent(self, event):
        if self.onMouseDoubleClickEvent:
            mb = MouseButton(event.button())  # mb: mouse button

            self.onMouseDoubleClickEvent(self, mb)

    def setOnContextMenu(self, func):
        self.onContextMenuEvent = func

    def contextMenuEvent(self, event):
        if self.onContextMenuEvent:
            self.onContextMenuEvent(self, event)

    # ---------------------- Events

    def show(self):
        super().show()

    def hide(self):
        super().hide()

    def tabifyDock(self, parent, child):
        return super().tabifyDockWidget(parent, child)

    # Type: Any QtWidget
    # Text: visible text on that QtWidget
    def findChild(self, type_, text):
        new_action = super().findChild(type_, text)
        if new_action:
            new_action.setText("Clicked New")

    def setStyle(self, style):
        self.setStyleSheet(style)

    def addToolbarBreak(self):
        self.addToolBarBreak()

    def getStandardIcons(self):
        """Returns sorted list of all valid QStyle.StandardPixmap enum names.

        Guaranteed to return names starting with 'SP_' prefix.
        """
        return Converter.to_lua_table(
            sorted(
                name
                for name in dir(QStyle.StandardPixmap)
                if name.startswith("SP_")
                and isinstance(getattr(QStyle.StandardPixmap, name), int)
            )
        )

    def getStandardIcon(self, icon_name) -> QIcon:
        # Get icon from style
        style = self.style()
        enum_value = getattr(QStyle.StandardPixmap, icon_name)
        icon = style.standardIcon(enum_value)
        return icon
