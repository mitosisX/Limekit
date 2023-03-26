# 
# from project Abigail 
#   - Every code I write falls under "project Abigail"
# 
# This is Miranda framework, named after one of Neptune's moon, simply because
# of it's destinct features (uniqueness).
# 
# 25 November, 2022 (11:25 am) UCT +02:00 Malawi, Africa
# Re-writing this after the first working source-code got lost
# P.S: Neglegence to utilize github's power
# 
# 

# The Lua interpreter
import lupa
from lupa import LuaRuntime

import sys
import os

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
from framework.controls.widgets.calendar import Calendar
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

from framework.handler.theming.themer import Theme
from framework.handler.system.clipboard import Clipboard
from framework.handler.system.timer import Timer
from framework.handler.system.cmdargs import CMD

from framework.handler.system.file import File
from framework.handler.system.paths import Paths
from framework.handler.system.taskbar_progress import TaskbarProgress
from framework.handler.system.notifcation import Notification
from framework.handler.system.tray import Tray

from framework.controls.dockers.menu.menu import Menu
from framework.controls.dockers.menu.menuitem import MenuItem
from framework.controls.dockers.menubar.menubar import Menubar

from framework.controls.widgets.containers.tab import Tab
from framework.controls.widgets.containers.tabitem import TabItem
from framework.controls.widgets.fluent.folderlist import FolderList

# Playground code
# from playground.fromtemplate import TemplateGenerator

#  use
# pyqtdarktheme
# qdarkstyle
#

# gets the path for the user files
src = os.path.join(os.getcwd(), 'source')

def images(path):
    global src
    return os.path.join(src, 'images', path)

def scripts(path):
    global src
    return os.path.join(src, 'scripts', path)

app = App()

"""
All keys marked by __ signify that I do not intent them to be accessed directly by the user
but by some internal JS function
"""
# objects = {
#     # 'app': MirandaApp,
#     'scripts': scripts,
#     'images': images,
#     '__file': File,
#     # 
#     # 
#     # 
#     'Window': Window,
#     'Button': Button,
#     'CheckBox': CheckBox,
#     'RadioButton': RadioButton,
#     'Label': Label,
#     'ComboBox': ComboBox,
#     'Layout': OLayout,
#     'GridLayout': GridLayout,
#     'Spinner': SpinBox,
#     'InputDialog': InputDialog,
#     'ProgressBar': ProgressBar,
#     'Slider': Slider,
#     'TextEdit': TextEdit,
#     'ListBox': ListBox,
#     # 
#     # 
#     # 
#     'Theme': Style,  # Replace with class to access different theming styles
#     'themes': list_themes(),
#     'Menu': Menu,
#     'MenuItem': MenuItem,
#     'Dock': Dock,
#     'Toolbar': Toolbar,
#     'ToolbarButton': ToolbarButton,
#     'sqlite': sqlite3,
#     'len': len,
#     'alert': MessageBox,
#     'Timer': Timer,
#     'cmd': CMD,
#     'Clipboard': Clipboard,
#     'SysTray': Tray,
    
#     'DDialog': DDialog,
#     '__aPopup': AboutPopup,
#     '__cPopup': CriticalPopup,
#     '__iPopup': InformationPopup,
#     '__qPopup': QuestionPopup,
#     '__wPopup': WarningPopup,
#     'Segmenter': Segmenter,
#     'TaskbarProgress': TaskbarProgress,
#     'Tab': Tab,
#     'TabItem':TabItem,
#     'List': FolderList,
    
#     'Notification': Notification,
#     '__paths': Paths,
#     # 'console.log': print,
#     # 'print': print,
#     # 'str': str,
#     # 'eval': eval,
#     # 
#     # 
#     # 'TestMenu': TemplateGenerator
# }

# After months of failing to understand the lupa framework and also how
# to call python objects in Lua
# 23 March, 2023 07:16 AM (UTC+02:00) Monday

lua = LuaRuntime(unpack_returned_tuples=True)

lua.globals().Window = Window
lua.globals().Button = Button
lua.globals().Label = Label
lua.globals().Segmenter = Segmenter
lua.globals().ListBox = ListBox
lua.globals().TextEdit = TextEdit
lua.globals().GridLayout = GridLayout
lua.globals().Layout = OLayout
lua.globals().Slider = Slider
lua.globals().Menu = Menu
lua.globals().MenuItem = MenuItem
lua.globals().Timer = Timer
lua.globals().Notification = Notification
lua.globals().SysTray = Tray
lua.globals().Toolbar = Toolbar
lua.globals().ToolbarButton = ToolbarButton
lua.globals().ComboBox = ComboBox
lua.globals().ProgressBar = ProgressBar
lua.globals().Spinner = SpinBox
lua.globals().Tab = Tab
lua.globals().TabItem = TabItem

lua.globals().Theme = Theme
lua.globals().str = str
lua.globals().eval = eval
lua.globals().images = images
lua.globals().scripts = scripts

lua_code = open(scripts('calculator.lua'), 'r').read()

lua.execute(lua_code)

sys.exit(app.execute())