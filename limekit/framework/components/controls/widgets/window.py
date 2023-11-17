import lupa

from PySide6.QtWidgets import QMainWindow, QWidget
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QIcon, QCursor, QPixmap

from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.components.controls.dockers.dockerwidget.docker import Docker
from limekit.framework.core.runner.app import App


class Window(QMainWindow, EnginePart):
    just_shown = False  # To be used for any first launch logic: center()...
    onShownEvent = None
    onResizeEvent = None
    onCloseEvent = None
    onResizeEvent = None

    @lupa.unpacks_lua_table
    def __init__(self, kwargs={}):
        super().__init__()

        self.setTitle(kwargs["title"]) if "title" in kwargs else self.setTitle(
            "Limekit - lua framework"
        )

        # if "title" in kwargs:
        #     self.setTitle(kwargs["title"])
        # else:
        #     self.setTitle("Limekit - lua framework")

        if "size" in kwargs:
            try:
                width, height = kwargs["size"].values()
                self.setSize(width, height)
            except ValueError as ex:
                self.setSize(500, 500)

                # print("Error: Not all sizes provided. Using {500, 500}")
        else:
            self.setSize(500, 500)

        if "location" in kwargs:
            location = kwargs["location"]
            pos = len(location)

            if pos == 2:
                x, y = location.values()

                self.move(x, y)
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

    def setMainWidget(self, child: QWidget):
        self.setCentralWidget(None)
        self.setCentralWidget(child)

    def setSize(self, width, height):
        self.resize(width, height)

    def setMinSize(self, width, height):
        self.setMinimumSize(width, height)

    def setMinHeight(self, height):
        self.setMinimumHeight(height)

    def setMinWidth(self, width):
        self.setMinimumWidth(width)

    def setLocation(self, x, y):
        self.move(x, y)

    # def addChild(self, *children):
    #     for child in children:
    #         self.layout.addWidget(child)
    #         self.layout.addStretch()

    def setLayout(self, layout):
        self.widget.setLayout(layout)
        # self.layout.addLayout(layout)

    def addDock(self, area, dock):
        self.addDockWidget(dock, self.__setDockArea(area))

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
            return Qt.LeftDockWidgetArea
        elif selected_area == "right":
            return Qt.RightDockWidgetArea
        elif selected_area == "top":
            return Qt.TopDockWidgetArea
        elif selected_area == "bottom":
            return Qt.BottomDockWidgetArea

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
    Dock: namespace - components.controls.dockers.dockerwidget.docking
    
    The Dock can accept parent in it's constructor, and using this makes the dock
    take up the whole are as this essentially makes the "central widget" of its parent
    
    While in this case, this method allows individual Docks to be added to the Window
    """

    def addDock(self, dock: Docker, area="left"):
        dock_area = Qt.LeftDockWidgetArea

        if area == "left":
            dock_area = Qt.LeftDockWidgetArea

        elif area == "right":
            dock_area = Qt.RightDockWidgetArea

        elif area == "top":
            dock_area = Qt.TopDockWidgetArea

        elif area == "bottom":
            dock_area = Qt.BottomDockWidgetArea

        self.addDockWidget(dock_area, dock)

    def center(self):
        qr = self.frameGeometry()
        cp = App.app.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def getSize(self):
        return self.size().width(), self.size().height()

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

    # ---------------------- Events

    def show(self):
        super().show()

    # Type: Any QtWidget
    # Text: visible text on that QtWidget
    def findChild(self, type_, text):
        new_action = super().findChild(type_, text)
        if new_action:
            new_action.setText("Clicked New")
