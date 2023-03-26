from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QStyleFactory
from PySide6.QtCore import Qt, QFile

from framework.controls.dockers.toolbar.toolbar import Toolbar
from framework.controls.dockers.dockerwidget.docking import Docker

from framework.kernel.runner.app import App
from PySide6.QtGui import QAction, QScreen, QIcon
from PySide6.QtWidgets import QApplication

class Window(QMainWindow):
    def __init__(self, title="MirandaJS - Active Apps"):
        super().__init__()
        self.widget = QWidget()

        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        # self.setGeometry(500, 100, 500, 500)
        
        # self.setSize(width, height)
        # self.center()
        
        self.setTitle(title)

    def setTitle(self, title):
        self.setWindowTitle(title)
        
    def setCentralChild(self, child):
        self.setCentralWidget(child)

    def setSize(self, width, height):
        self.resize(width, height)

    def setLocation(self, x, y):
        self.move(x, y)

    def addChild(self, *children):
        for child in children:
            self.layout.addWidget(child)
            # self.layout.addStretch()

    def setLayout(self, *layouts: QWidget):
        for each_layout in layouts:
            self.layout.addLayout(each_layout.layout)
            
    def addDock(self, pos, dock):
        self.addDockWidget(dock, pos)

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

    def setMenubar(self, menu):
        self.setMenuBar(menu)
        
    """
    Dock: namespace - core.dockers.dockwidgets.docker.Dock
    
    The Dock can accept parent in it's constructor, and using this makes the dock
    take up the whole are as this essentially makes the "central widget" of its parent
    
    While in this case, this method allows individual Docks to be added to the Window
    """
    def addDock(self, dock: Docker, area = 'left'):
        dock_area = Qt.LeftDockWidgetArea
            
        if area == 'left':
            dock_area = Qt.LeftDockWidgetArea
            
        elif area == 'right':
            dock_area = Qt.RightDockWidgetArea
            
        elif area == 'top':
            dock_area = Qt.TopDockWidgetArea
            
        elif area == 'bottom':
            dock_area = Qt.BottomDockWidgetArea
        
        self.addDockWidget(dock_area, dock)
        
    def center(self):
        center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        geo = self.frameGeometry()
        geo.moveCenter(center)
        self.move(geo.topLeft())