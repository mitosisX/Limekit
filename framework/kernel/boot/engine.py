"""
20 March, 2023 8:23 AM (Monday) (UTC+02:00)

The code is a mess, I know.... get over it... or simply fix it ;-)
"""

import js2py
from js2py import base
import sys
import os
import sqlite3

from PySide6.QtWidgets import QApplication, QWidget
from qt_material import apply_stylesheet
from qt_material import list_themes
from framework.controls.dockers.menu.menuitem import MenuItem
from framework.controls.dockers.toolbar.toolbar_button import ToolbarButton
from framework.controls.dockers.dockerwidget.docking import Docker

# COllection of userful utilities
# from framework.handler.scripts.miranda import MirandaApp

# Tis is the class that controls the whole application
# event loop
from framework.kernel.runner.app import App
 
from framework.controls.widgets.button import Button
from framework.controls.widgets.checkbox import CheckBox
from framework.controls.widgets.radiobutton import RadioButton
from framework.controls.widgets.label import Label
from framework.controls.widgets.window import Window
from framework.controls.widgets.combobox import ComboBox
from framework.controls.widgets.layouts.olayout import OLayout
from framework.controls.widgets.layouts.grid import GridLayout
from framework.controls.widgets.spinbox import SpinBox
from framework.controls.widgets.progressbar import ProgressBar
from framework.controls.widgets.slider import Slider
from framework.controls.widgets.textedit import TextEdit
from framework.controls.widgets.listbox import ListBox

from framework.controls.widgets.segmenter import Segmenter
from framework.controls.dockers.toolbar.toolbar import Toolbar
from framework.controls.dialogs.messagebox import MessageBox
from framework.controls.dialogs.inputdialog import InputDialog
from framework.controls.dialogs.ddialog import DDialog

from framework.controls.dialogs.popups.about_popup import AboutPopup
from framework.controls.dialogs.popups.critical_popup import CriticalPopup
from framework.controls.dialogs.popups.information_popup import InformationPopup
from framework.controls.dialogs.popups.question_popup import QuestionPopup
from framework.controls.dialogs.popups.warning_popup import WarningPopup

from framework.handle.theming.material.theme import MaterialStyle
from framework.handle.system.clipboard import Clipboard
from framework.handle.system.timer import Timer
from framework.handle.system.cmdargs import CMD

from framework.handle.system.file import File
from framework.handle.system.paths import Paths
from framework.handle.system.taskbar_progress import TaskbarProgress
from framework.handle.system.notifcation import Notification
from framework.handle.system.tray import Tray

from framework.controls.dockers.menu.menu import Menu
from framework.controls.dockers.menu.menuitem import MenuItem
from framework.controls.dockers.menubar.menubar import Menubar

from framework.controls.widgets.containers.tab import Tab
from framework.controls.widgets.containers.tabitem import TabItem
from framework.controls.widgets.fluent.folderlist import FolderList

class Engine:
    def __init__(self):
        self.__pyObjects = {}
        
        self.engine = None #holds the js2py context
        self.app = App() # holds the PySide6 application
        
    def init_JsEngine(self):
        self.engine = js2py.EvalJs(self.__pyObjects, enable_require=True)
        
    def start(self, other_function):
        # if there's anything user wants to execute before the engine initiates, pass the function
        if other_function:
            other_function()
        self.setRenderEngine()
        self.initJsEngine()
        
    """
    For executing any incoming JavaScript code
    """
    def execute(self, JsScript):
        self.engine.execute(JsScript)
    
    def set_object(self, **object):
        self.pyObjects.update
        
    def set_eventloop(self):
        sys.exit(self.app.execute())
        
    def images(self, path):
        global src
        return os.path.join(
            src, 'images',
            path.to_string().value if type(path) == base.PyJsString else path)

    def scripts(self, path):
        global src
        return os.path.join(
            src, 'scripts',
            path.to_string().value if type(path) == base.PyJsString else path)
        
    
    # To be used for plugin intialization
    # manager = PluginManager()
    # manager.load_plugins()
    # manager.activate_plugins()