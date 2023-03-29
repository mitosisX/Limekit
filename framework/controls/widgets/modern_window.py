from qtmodern import windows
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QStyleFactory
from PySide6.QtCore import Qt, QFile

from framework.controls.dockers.toolbar.toolbar import Toolbar
from framework.controls.dockers.dockerwidget.docking import Docker

from framework.kernel.runner.app import App
from PySide6.QtGui import QAction, QScreen, QIcon
from PySide6.QtWidgets import QApplication

class ModernWindow(windows.ModernWindow):
    def __init__(self, parent):
        super().__init__(parent)