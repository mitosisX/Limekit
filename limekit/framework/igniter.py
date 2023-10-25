#
# from project Abigail
#   - Every code I write falls under "project Abigail"
#
# This is Miranda JS framework, named after one of Neptune's moon, simply because
# of it's destinct features (uniqueness).
#
# 25 November, 2022 (11:25 am) (UTC+02:00) Malawi, Africa
# Re-writing this after the first working source-code got lost
# P.S: Neglegence to utilize github's power
#
#

import js2py
from js2py import base
import sys
import os
import sqlite3

from PySide6.QtWidgets import QApplication, QWidget
from qt_material import apply_stylesheet
from qt_material import list_themes
from limekit.framework.components.controls.dockers.menu.menuitem import MenuItem
from limekit.framework.components.controls.dockers.toolbar.toolbar_button import (
    ToolbarButton,
)
from limekit.framework.components.controls.dockers.dockerwidget.docking import Docker

# COllection of userful utilities
# from limekit.framework.handler.scripts.limekit import limekitApp

# Tis is the class that controls the whole application
# event loop
from limekit.framework.core.runner.app import App

from limekit.framework.components.controls.widgets.button import Button
from limekit.framework.components.controls.widgets.checkbox import CheckBox
from limekit.framework.components.controls.widgets.calendar import Calendar
from limekit.framework.components.controls.widgets.groupbox import GroupBox
from limekit.framework.components.controls.widgets.table import TableGrid
from limekit.framework.components.controls.widgets.radiobutton import RadioButton
from limekit.framework.components.controls.widgets.label import Label
from limekit.framework.components.controls.widgets.window import Window
from limekit.framework.components.controls.widgets.combobox import ComboBox
from limekit.framework.components.layouts.olayout import OLayout
from limekit.framework.components.layouts.vlayout import VerticalLayout
from limekit.framework.components.layouts.hlayout import HorizontalLayout
from limekit.framework.components.layouts.grid import GridLayout
from limekit.framework.components.controls.widgets.spinbox import SpinBox
from limekit.framework.components.controls.widgets.progressbar import ProgressBar
from limekit.framework.components.controls.widgets.slider import Slider
from limekit.framework.components.controls.widgets.textfield import TextEdit
from limekit.framework.components.controls.widgets.listbox import ListBox

from limekit.framework.components.controls.widgets.segmenter import Segmenter
from limekit.framework.components.controls.dockers.toolbar.toolbar import Toolbar
from limekit.framework.components.controls.dialogs.messagebox import MessageBox
from limekit.framework.components.controls.dialogs.inputdialog import InputDialog
from limekit.framework.components.controls.dialogs.ddialog import DDialog

from limekit.framework.components.controls.dialogs.popups.about_popup import AboutPopup
from limekit.framework.components.controls.dialogs.popups.critical_popup import (
    CriticalPopup,
)
from limekit.framework.components.controls.dialogs.popups.information_popup import (
    InformationPopup,
)
from limekit.framework.components.controls.dialogs.popups.question_popup import (
    QuestionPopup,
)
from limekit.framework.components.controls.dialogs.popups.warning_popup import (
    WarningPopup,
)

from limekit.framework.handle.theming.themes.themer import Theme
from limekit.framework.handle.system.clipboard import Clipboard
from limekit.framework.handle.system.timer import Timer
from limekit.framework.handle.system.cmdargs import CMD

from limekit.framework.handle.system.file import File
from limekit.framework.handle.system.paths import Paths
from limekit.framework.handle.system.taskbar_progress import TaskbarProgress
from limekit.framework.handle.system.notifcation import Notification
from limekit.framework.handle.system.tray import Tray

from limekit.framework.components.controls.dockers.menu.menu import Menu
from limekit.framework.components.controls.dockers.menu.menuitem import MenuItem
from limekit.framework.components.controls.dockers.menubar.menubar import Menubar

from limekit.framework.components.controls.widgets.containers.tab import Tab
from limekit.framework.components.controls.widgets.containers.tabitem import TabItem
from limekit.framework.components.controls.widgets.fluent.folderlist import FolderList

# Playground code
# from playground.fromtemplate import TemplateGenerator

#  use
# pyqtdarktheme
# qdarkstyle
#

from win11toast import toast

# gets the path for the user files
src = os.path.join(os.getcwd(), "source")


def images(path):
    global src
    return os.path.join(
        src, "images", path.to_string().value if type(path) == base.PyJsString else path
    )


def scripts(path):
    global src
    return os.path.join(
        src,
        "scripts",
        path.to_string().value if type(path) == base.PyJsString else path,
    )


app = App()

"""
All keys marked by __ signify that I do not intent them to be accessed directly by the user
but by some internal JS function
"""
objects = {
    # 'app': limekitApp,
    "scripts": scripts,
    "images": images,
    "__file": File,
    "toast": toast,
    #
    #
    #
    "Window": Window,
    "Button": Button,
    "Calendar": Calendar,
    "CheckBox": CheckBox,
    "RadioButton": RadioButton,
    "Label": Label,
    "ComboBox": ComboBox,
    "Layout": OLayout,
    "GridLayout": GridLayout,
    "Spinner": SpinBox,
    "InputDialog": InputDialog,
    "ProgressBar": ProgressBar,
    "Slider": Slider,
    "TextEdit": TextEdit,
    "ListBox": ListBox,
    "VLayout": VerticalLayout,
    "HLayout": HorizontalLayout,
    "GroupBox": GroupBox,
    "TableGrid": TableGrid,
    #
    #
    #
    "Theme": Theme,  # Replace with class to access different theming styles
    "themes": list_themes(),
    "Menu": Menu,
    "MenuItem": MenuItem,
    "Menubar": Menubar,
    "Dock": Docker,
    "Toolbar": Toolbar,
    "ToolbarButton": ToolbarButton,
    "sqlite": sqlite3,
    "len": len,
    "alert": MessageBox,
    "Timer": Timer,
    "cmd": CMD,
    "Clipboard": Clipboard,
    "SysTray": Tray,
    "DDialog": DDialog,
    "__aPopup": AboutPopup,
    "__cPopup": CriticalPopup,
    "__iPopup": InformationPopup,
    "__qPopup": QuestionPopup,
    "__wPopup": WarningPopup,
    "Segmenter": Segmenter,
    "TaskbarProgress": TaskbarProgress,
    "Tab": Tab,
    "TabItem": TabItem,
    "List": FolderList,
    "Notification": Notification,
    "__paths": Paths,
    "console.log": print,
    "print": print,
    "str": str,
    "eval": eval,
    #
    #
    # 'TestMenu': TemplateGenerator
}

context = js2py.EvalJs(objects, enable_require=True)

# The main entry file of the user's JS file

app_code = open("framework\scripts\limekit.js", "r").read()
js_code = open(scripts("tablegrid.js"), "r").read()

context.execute(app_code)
context.execute(js_code)

sys.exit(app.execute())
