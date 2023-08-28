from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QStyleFactory
from PySide6.QtCore import Qt

from limekit.framework.core.engine.parts import EnginePart

from limekit.framework.components.controls.dockers.toolbar.toolbar import Toolbar
from limekit.framework.components.controls.dockers.dockerwidget.docking import Docker

from limekit.framework.core.runner.app import App
from PySide6.QtGui import QAction, QScreen, QIcon
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QUrl

# from limekit.framework.handler.plugins.plugin_manager import PluginManager


class Window(EnginePart, QMainWindow):
    def __init__(self, title="limekit - lua framework"):
        super().__init__()

        self.widget = QWidget()
        self.setCentralWidget(self.widget)

        # self.setGeometry(500, 100, 500, 500)

        self.setSize(500, 300)

        self.center()

        self.setTitle(title)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setMainWidget(self, child):
        self.setCentralWidget(child)

    def setSize(self, width, height):
        self.resize(width, height)

    def setLocation(self, x, y):
        self.move(x, y)

    def addChild(self, *children):
        for child in children:
            self.layout.addWidget(child)
            self.layout.addStretch()

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

    def getStyles(self):
        return QStyleFactory.keys()

    """
    Platform-dependent Styles obtained from getStyles() method
    """

    def setStyle(self, style):
        App.app.setStyle(style)

    def setIcon(self, icon):
        self.setWindowIcon(QIcon(icon))

    def addToolbar(self, toolbar: Toolbar):
        self.addToolBar(toolbar)

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
        desktop = QApplication.primaryScreen().size()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def show(self):
        super().show()
