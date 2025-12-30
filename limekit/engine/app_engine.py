# Limekit Engine - The core of the framework

import re
import os
import sys
import inspect
import importlib

# from xlsxwriter import Workbook

from playsound import playsound

import lupa
from lupa import LuaRuntime
from PySide6.QtCore import QFileSystemWatcher

# from faker import Faker

from limekit.config import settings
from limekit.engine.parts import EnginePart

# Was experiencing circular import in Converter, thats why I am separating the engine for global use
from limekit.engine.globals.global_engine import GlobalEngine
from limekit.utils.converters import Converter
from limekit.engine.lifecycle.app import App

from limekit.utils.path import Path
from limekit.utils.file import File
from limekit.utils.fileutils import FileUtils

from limekit.core.routing.routes import Routing

from limekit.lua.script import Script
from limekit.engine.parser.lua_parser import LuaParser
from limekit.engine.lifecycle.shutdown import destroy_engine


# Limekit Engine Class
# This is where all the magic happens. The Engine is the core of the framework,
# responsible for executing lua code and managing the application lifecycle.


class Engine:
    def __init__(self):
        self.projects_dir = ""

        self.app = App()  # holds the PySide6 QApplication
        self.routing = Routing()

        self.limekit_root_dir = settings.limekit_SITEPACKAGE_DIR

        # code for perfomance testing, didn'yt work out
        # only the widgets or corresponding widget items to be loaded will be stored here
        # self.loaded_user_classes = set()

        # self.plugin_manager = PluginManager()  # The code that init all user plugins

        self.engine = None  # holds the lua engine
        self.file_watcher = None  # The file watcher responsible for code injection

    # These shall serve as property access constraints
    def _getter_restric(self, obj, attr_name):
        if attr_name != "name":
            return getattr(obj, attr_name)

    def _setter_restric(self, obj, attr_name, value):
        if attr_name != "put":
            setattr(obj, attr_name, value)
            return

    # Init the lua engine
    def init_lua_engine(self):
        self.engine = LuaRuntime(
            unpack_returned_tuples=True,
            # attribute_handlers=(self._getter_restric, self._setter_restric),
        )
        GlobalEngine.global_engine = self.engine

    # Called after instantiating the Engine
    def start(self):
        # self.fix_vital_dirs() # Unnecessary, handled by the runner and the future build engine
        # self.init_plugins()  # Has to load first coz we don't walk the engine to run with only our py objects

        self.init_lua_engine()  # Set the py objects to the engine
        # self.scan_user_project_classes()
        # loads all required classes from INSTALLED_APPS and additional method
        self.gather_lua_engine_objects()
        self.set_custom_lua_require_path()

        self.init_routing_system()

        # everything that is IDE specific, invokes from inside here
        self.init_ide_only_features()

        self.execute_vital_lua()  # Execute limekit.lua to enable app access
        self.execute_main_lua()  # execute user entry point file
        self.set_eventloop()  # Set the PySide6 mainloop running. VITAL!!!!!!

    # Tailwind-like architecture: only load the classes available in the user's code for better perfomance
    def scan_user_project_classes(self):
        lua_parser = LuaParser()

        for root, dirs, files in os.walk(Path.scripts_dir()):
            for file in files:
                if file.endswith(".lua"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as file:
                            content = file.read()

                        all_classes = lua_parser.get_all_classes(content)

                        for class_name in all_classes:
                            self.loaded_user_classes.add(class_name)

                    except FileNotFoundError:
                        from limekit.core.error_handler import warn
                        warn(f"File '{file_path}' not found during class scanning", "AppEngine")
                        return
                    except Exception as e:
                        from limekit.core.error_handler import warn
                        warn(f"Error reading file during class scanning: {e}", "AppEngine")
                        return

        self.loaded_user_classes.add("Window")
        self.loaded_user_classes.add("Spacer")
        self.loaded_user_classes.add("Separator")

    def init_code_injection_vars(self):
        self.code_injection_dir = Path.join_paths(
            self.projects_dir, ".limekit"
        )  # The dir where the code injection file is created
        self.code_injection_file = Path.join_paths(
            self.code_injection_dir, "_code.lua"
        )  # The file for the code to be injected

    # Any features needed in IDE modeshould be
    def init_ide_only_features(self):
        if not self.isIDE():  # if not in IDE mode, do nothing
            return

        # The project_path is always blank when the IDE is not executing an app
        # REFER: limekit.framework.core.mechanism.boot.starter.ProjectRunner
        if Path.project_path:
            # The path that we received from ProcessRunner, this is the path to the project to be executed,
            # but all we want is the root dir, and not the dir itself
            self.projects_dir = Path.get_parent_dir(Path.project_path)

            self.init_code_injection_vars()  # set the code injection vars
            self.init_code_injection()

    #   Code injection feature: Implemented on 14 April, 2025 (4:57 PM, UTC+2)
    #
    #   The current "logic" is simple: create a file when user intends to inject code, read from file,
    #   store in memory, delete file and execute it -- .limekit/_code.lua
    #
    # FileSystemWatcher watches .limekit dir for _code.lua
    def init_code_injection(self):
        self.create_injection_dir()  # create the dir first

        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.addPath(self.code_injection_dir)
        self.file_watcher.directoryChanged.connect(
            self.handle_code_injection_file_present
        )

    # Create the .limekit dir before watching it
    def create_injection_dir(self):
        if not Path.check_path(self.code_injection_dir):
            Path.make_dir(self.code_injection_dir)

    # This method is called when a file is created in the scripts dir
    def handle_code_injection_file_present(self, path):
        if Path.check_path(self.code_injection_file):
            code = File.read_file(self.code_injection_file)
            self.execute_raw_script(code)

            File.remove_file(
                self.code_injection_file
            )  # delete the file after executing

    def init_routing_system(self):
        project_file = Path.project_file()
        project_file_json = FileUtils.read_file_json(project_file)

        self.routing.set_project_json(project_file_json)

    # All core lua code for the limekit framework
    def execute_vital_lua(self):
        # For frozen apps, look in _MEIPASS; otherwise use site-packages
        if self.isIDE():
            # Development mode - use installed limekit package
            limekit_lua_file = Path.join_paths(self.limekit_root_dir, "lua", "limekit.lua")
        else:
            # Frozen mode - use bundled limekit.lua from _MEIPASS
            limekit_lua_file = Path.join_paths(sys._MEIPASS, "limekit", "lua", "limekit.lua")

        limekit_file_content = File.read_file(limekit_lua_file)
        self.execute(limekit_file_content)

    """
    For executing any incoming lua code
    
    Has to redesigned to determine whether or not the framework is being run after freeze or in "IDE"
    """

    def execute(self, lua_content):
        self.engine.execute(lua_content)

    def evaluate(self, content):
        return self.engine.eval(content)

    # Evaluates a lua script and returns the result
    def eval(self, script):
        return self.engine.eval(script)

    # The user's main.lua entry point code
    def execute_main_lua(self):
        path_to_main = Path.scripts("main.lua")
        # print("### ", Path.project_path)

        try:
            main_lua_content = File.read_file(path_to_main)
            self.execute(main_lua_content)
        except FileNotFoundError as ex:
            from limekit.core.error_handler import handle_exception
            handle_exception(ex, context="EntryPoint", fatal=True)
            print("\nEntryPointError: No main.lua file found in scripts directory")
            destroy_engine()

    # The PySide6 engine that handles the mainloop of the program
    def set_eventloop(self):
        self.app.execute()

    def _get_all_subdirectories(self, root_path):
        """Recursively get all subdirectories of a path."""
        subdirs = []
        if not os.path.exists(root_path):
            return subdirs

        for root, dirs, files in os.walk(root_path):
            # Add the root itself
            subdirs.append(root)

        return subdirs

    def _normalize_lua_path(self, path):
        """Normalize a path for Lua's package.path (forward slashes, no trailing slash)."""
        return os.path.normpath(path).replace("\\", "/").rstrip("/")

    def set_custom_lua_require_path(self):
        """
        Sets custom Lua require paths for both development and frozen (packaged) modes.

        Features:
        - Works in both IDE (development) and frozen (PyInstaller) modes
        - Adds all subdirectories of scripts/ and misc/ to package.path
        - Supports init.lua pattern (require "folder" finds folder/init.lua)
        - Handles .require file with relative paths (frozen-compatible)
        - Works across all operating systems (Windows, macOS, Linux)

        In frozen mode:
        - Absolute paths in .require are skipped (they won't exist)
        - Relative paths are resolved against the bundle directory
        - All script subdirectories are automatically included
        """
        lua_path_entries = []
        project_root = Path.project_path
        is_frozen = not self.isIDE()

        # Get base directories
        scripts_path = self._normalize_lua_path(Path.scripts_dir())
        misc_path = self._normalize_lua_path(Path.misc_dir())

        # Add main directories with both ?.lua and ?/init.lua patterns
        # This allows: require "module" AND require "folder" (finds folder/init.lua)
        lua_path_entries.append(f"{scripts_path}/?.lua")
        lua_path_entries.append(f"{scripts_path}/?/init.lua")
        lua_path_entries.append(f"{misc_path}/?.lua")
        lua_path_entries.append(f"{misc_path}/?/init.lua")

        # Add ALL subdirectories of scripts/ and misc/ to support nested requires
        # This allows files in subdirectories to require siblings without full paths
        # e.g., in scripts/gui/modals/dialog.lua: require "utils" finds scripts/gui/modals/utils.lua
        for subdir in self._get_all_subdirectories(Path.scripts_dir()):
            normalized = self._normalize_lua_path(subdir)
            if normalized != scripts_path:  # Don't duplicate the root
                lua_path_entries.append(f"{normalized}/?.lua")
                lua_path_entries.append(f"{normalized}/?/init.lua")

        for subdir in self._get_all_subdirectories(Path.misc_dir()):
            normalized = self._normalize_lua_path(subdir)
            if normalized != misc_path:  # Don't duplicate the root
                lua_path_entries.append(f"{normalized}/?.lua")

        # Process .require file if it exists
        req_file_path = os.path.join(project_root, ".require")
        if Path.check_path(req_file_path):
            try:
                require_content = File.read_file(req_file_path)

                # Split paths by semicolon or newline
                raw_paths = []
                if ";" in require_content:
                    raw_paths = [p.strip() for p in require_content.split(";") if p.strip()]
                else:
                    raw_paths = [p.strip() for p in require_content.split("\n") if p.strip()]

                for path in raw_paths:
                    normalized_path = path.replace("\\", "/").rstrip("/")

                    # Check if path is absolute
                    is_absolute = os.path.isabs(path) or (len(path) > 1 and path[1] == ':')

                    if is_frozen and is_absolute:
                        # In frozen mode, skip absolute paths - they won't exist
                        # Users should use relative paths for frozen-compatible requires
                        from limekit.core.error_handler import warn
                        warn(f"Skipping absolute require path in frozen mode: {path}", "AppEngine")
                        continue
                    elif not is_absolute:
                        # Relative path - resolve against project root
                        resolved = os.path.join(project_root, path)
                        normalized_path = self._normalize_lua_path(resolved)

                    # Only add if the path exists
                    if os.path.exists(normalized_path.replace("/", os.sep)):
                        lua_path_entries.append(f"{normalized_path}/?.lua")
                        lua_path_entries.append(f"{normalized_path}/?/init.lua")

            except Exception as e:
                from limekit.core.error_handler import warn
                warn(f"Failed to process .require file: {e}", "AppEngine")

        # Combine all paths and set package.path
        if lua_path_entries:
            # Remove duplicates while preserving order
            seen = set()
            unique_paths = []
            for p in lua_path_entries:
                if p not in seen:
                    seen.add(p)
                    unique_paths.append(p)

            paths_string = ";".join(unique_paths) + ";"
            lua_command = "package.path = '{}' .. package.path".format(paths_string)
            self.execute(lua_command)

    """
    Load and intialize all plugins from the user
    """

    def init_plugins(self):
        self.plugin_manager.load_plugins()
        self.plugin_manager.activate_plugins()

        self.set_objects(self.plugin_manager.plugin_pyobjects())

    # In case of any missing dirs, this method rereates them
    def fix_app_folders(self):
        pass

    # Check if app is running in IDE mode
    def isIDE(self):
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            # print("running in a PyInstaller bundle")
            return False
        else:
            return True
            # print("running in a normal Python process")

    def gather_lua_engine_objects(self):
        self.gather_from_dirs()
        self.gather_additional_parts()

    # This method walks through all dir specified in in the settings.py INSTALLED_PARTS
    def gather_from_dirs(self):
        if self.isIDE():
            # Development mode - walk filesystem to discover classes
            walked_classes = []

            for app in settings.INSTALLED_PARTS:
                app_path = Path.dot_path(app)
                limekit_dir = Path.get_parent_dir(settings.limekit_SITEPACKAGE_DIR)
                full_path = os.path.join(limekit_dir, app_path)

                files_obtained = Path.walk_dir_get_files(full_path)
                walked_classes += files_obtained

            self.load_classes(walked_classes)
        else:
            # Frozen mode - use pkgutil to discover bundled modules
            self._load_frozen_classes()

    def _load_frozen_classes(self):
        """Load limekit classes in frozen mode by explicitly importing all modules."""
        # Explicit list of all modules containing EnginePart subclasses
        # This is necessary because pkgutil.walk_packages doesn't work reliably in frozen apps
        frozen_modules = [
            # Layouts
            "limekit.components.layouts.vlayout",
            "limekit.components.layouts.hlayout",
            "limekit.components.layouts.grid",
            "limekit.components.layouts.formlayout",
            "limekit.components.layouts.stackedlayout",
            # Widgets
            "limekit.components.widgets.button",
            "limekit.components.widgets.label",
            "limekit.components.widgets.lineedit",
            "limekit.components.widgets.textfield",
            "limekit.components.widgets.checkbox",
            "limekit.components.widgets.radiobutton",
            "limekit.components.widgets.combobox",
            "limekit.components.widgets.listbox",
            "limekit.components.widgets.slider",
            "limekit.components.widgets.progressbar",
            "limekit.components.widgets.spinner",
            "limekit.components.widgets.doublespinner",
            "limekit.components.widgets.table",
            "limekit.components.widgets.treewidget",
            "limekit.components.widgets.tree_widget",
            "limekit.components.widgets.groupbox",
            "limekit.components.widgets.splitter",
            "limekit.components.widgets.spacer",
            "limekit.components.widgets.separator",
            "limekit.components.widgets.image",
            "limekit.components.widgets.gifplayer",
            "limekit.components.widgets.window",
            "limekit.components.widgets.container",
            "limekit.components.widgets.scroller",
            "limekit.components.widgets.buttongroup",
            "limekit.components.widgets.commandbutton",
            "limekit.components.widgets.lcdnumber",
            "limekit.components.widgets.font_combobox",
            "limekit.components.widgets.accordion",
            "limekit.components.widgets.knob",
            "limekit.components.widgets.advanced_slider",
            "limekit.components.widgets.horizontal_line",
            "limekit.components.widgets.vertical_line",
            "limekit.components.widgets.slidingstackedwidget",
            # Container widgets
            "limekit.components.widgets.containers.tab",
            "limekit.components.widgets.containers.tabbar",
            "limekit.components.widgets.containers.tabitem",
            # Picker widgets
            "limekit.components.widgets.pickers.calendar",
            "limekit.components.widgets.pickers.datepicker",
            "limekit.components.widgets.pickers.timepicker",
            # Item widgets
            "limekit.components.widgets.items.tableitem",
            "limekit.components.widgets.items.treeview_item",
            # Menu
            "limekit.components.menu.menu",
            "limekit.components.menu.menuitem",
            "limekit.components.menu.dropmenu",
            "limekit.components.menubar.menubar",
            # Toolbar
            "limekit.components.toolbar.toolbar",
            "limekit.components.toolbar.toolbar_button",
            # Statusbar
            "limekit.components.statusbar.statusbar",
            # Dialogs
            "limekit.components.dialogs.modal",
            "limekit.components.dialogs.messagebox",
            "limekit.components.dialogs.openfile",
            "limekit.components.dialogs.savefile",
            "limekit.components.dialogs.folderpicker",
            "limekit.components.dialogs.font",
            "limekit.components.dialogs.color",
            "limekit.components.dialogs.error",
            "limekit.components.dialogs.print_preview",
            "limekit.components.dialogs.popups.alert_dialog",
            "limekit.components.dialogs.popups.about_popup",
            "limekit.components.dialogs.popups.critical_popup",
            "limekit.components.dialogs.popups.information_popup",
            "limekit.components.dialogs.popups.warning_popup",
            "limekit.components.dialogs.popups.question_popup",
            "limekit.components.dialogs.inputs.text_dialog",
            "limekit.components.dialogs.inputs.multiline_input",
            "limekit.components.dialogs.inputs.combobox_dialog",
            "limekit.components.dialogs.inputs.integer_input",
            "limekit.components.dialogs.inputs.double_input",
            # Dockable
            "limekit.components.dockable.dockable_widget",
            # Charts
            "limekit.components.charts.chart",
            "limekit.components.charts.chartview",
            "limekit.components.charts.categoryaxis",
            "limekit.components.charts.linegraph.linechart",
            "limekit.components.charts.bar.barchart",
            "limekit.components.charts.bar.barset",
            "limekit.components.charts.area.areachart",
            "limekit.components.charts.axis.valueaxis",
            # Core utilities
            "limekit.core.paths",
            "limekit.core.clipboard",
            "limekit.core.timer",
            "limekit.core.systemtray",
            "limekit.core.system_notifcation",
            "limekit.core.database.sqlite3",
            "limekit.core.bootstrap.subprocess_runner",
            "limekit.core.bootstrap.engine_launcher",
            # Utils
            "limekit.utils.path",
            "limekit.utils.file",
            "limekit.utils.sound",
            "limekit.utils.encoding",
            "limekit.utils.fileutils",
            "limekit.utils.sysutil",
            "limekit.utils.converters",
            "limekit.utils.validators",
            "limekit.utils.emoji_str",
            "limekit.utils.utils",
            "limekit.utils.sorter",
            # GUI utilities
            "limekit.gui.app_styles",
            "limekit.gui.font",
            "limekit.gui.keyboard",
            "limekit.gui.keyboard_shortcut",
            "limekit.gui.dropshadow",
            "limekit.gui.syntax_highlighter",
            "limekit.gui.threading",
            # Theming
            "limekit.core.theming.themes.themer",
            "limekit.core.theming.themes.material.theme",
            "limekit.core.theming.themes.darkstylesheet.theme",
            "limekit.core.theming.themes.darklight.theme",
            "limekit.core.theming.themes.qtthemes.theme",
            "limekit.core.theming.themes.misc.theme",
            "limekit.core.theming.palletes.palleting",
        ]

        for modname in frozen_modules:
            try:
                module = importlib.import_module(modname)

                # Find EnginePart subclasses in the module
                for name in dir(module):
                    obj = getattr(module, name)
                    if (
                        isinstance(obj, type)
                        and issubclass(obj, EnginePart)
                        and obj is not EnginePart
                    ):
                        object_name = obj.name if obj.name else obj.__name__
                        self.engine.globals()[object_name] = obj

            except Exception as e:
                from limekit.core.error_handler import warn
                warn(f"Failed to import {modname}: {e}", "AppEngine")

    def gather_additional_parts(self):
        """
        Some additional functions such as using len() in lua or anything required but not
        really that essential (well, some)
        """
        other_parts = {
            "scripts": Path.scripts,
            "images": Path.images,
            "misc": Path.misc,
            "__lua_execute_file": self.execute_from_file,
            "__lua_execute_raw_script": self.execute_raw_script,
            "__lua_evaluate": self.evaluate,
            # "fake": Faker(),
            # "Workbook": Workbook,
            "route": self.routing.fetch_resource,
            "Sound": playsound,
            # "Bar": Bar,
            # "requests": requests,
            # "BeautifulSoup": BeautifulSoup,
            "__engineState": self.isIDE,
            "len": len,
            # "dir": dir,
            "print": print,
            # --------- Data types
            "str": str,
            "dict": dict,
            "int": int,
            "tuple": tuple,
            "list": Converter.list_,
            "lua_table": Converter.to_lua_table,
            "zip": Converter.zip_,
            # Data types ---------
            "eval": eval,
            # "FluentIcon": FluentIcon,
            "__quit": self.__quit,
        }

        for obj_name, object_ in other_parts.items():
            self.engine.globals()[obj_name] = object_

    # Executes a lua file
    def execute_from_file(self, file):
        self.execute(File.read_file(file))

    # Executes raw lua code
    def execute_raw_script(self, lua_script):
        self.execute(lua_script)

    def __quit(self):
        self.app.app.instance().quit()

    # Hard way for filtering out classes to load
    def filter_out_load_classes_based_on_dir(self, full_path, search_path):
        normalized_full = os.path.normpath(full_path)
        normalized_sub = os.path.normpath(search_path)

        return normalized_sub in normalized_full

    # This is where all the magic of loading python classes to be used inside lua happens
    def load_classes(self, files):
        # print(self.loaded_user_classes)

        for file in files:
            the_path = os.sep.join(file.split(os.sep)[:-1])
            the_file = file.split(os.sep)[-1].split(".")[0]

            file_path = os.path.join(the_path, file.split(os.sep)[-1])

            # Create a spec for the module
            spec = importlib.util.spec_from_file_location(the_file, file_path)
            module = importlib.util.module_from_spec(spec)

            # Finalize the loading process
            spec.loader.exec_module(module)

            for name in dir(module):
                class_ = getattr(module, name)

                if (
                    isinstance(class_, type)
                    and issubclass(class_, EnginePart)
                    and class_ is not EnginePart
                ):
                    class_for_lua = class_

                    object_name = (
                        class_for_lua.name
                        if class_for_lua.name
                        else class_for_lua.__name__
                    )

                    # !not being used. Maybe later, but not now

                    # Now, the filtering out of widgets
                    # Considering that the widgets (memory consumers) are found in this dir,
                    # We need to only import the widgets found in the user's code
                    # if self.filter_out_load_classes_based_on_dir(
                    #     the_path, "components"
                    # ):
                    #     try:
                    #         if (
                    #             not object_name.startswith("__")
                    #             and not object_name in self.loaded_user_classes
                    #         ):
                    #             # print(object_name)
                    #             continue
                    #             # pass

                    #     except Exception as e:
                    #         pass
                    # print(e)
                    # print(file)

                    # Create the lua objects
                    # print(object_name)

                    self.engine.globals()[object_name] = class_for_lua


# 24 December, 2023 17:02 PM (Sunday)
class Build:
    # data refers to the limey props: name, version...
    def __init__(self, data=None):
        pass

    def copy_vital_dirs(self):
        pass

    def create_build_files_and_folders(self):
        pass
