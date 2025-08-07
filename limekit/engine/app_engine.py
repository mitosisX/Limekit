"""
         _     _                _    _ _     _____                                            _    
        | |   (_)_ __ ___   ___| | _(_) |_  |  ___| __ __ _ _ __ ___   _____      _____  _ __| | __
        | |   | | '_ ` _ \ / _ \ |/ / | __| | |_ | '__/ _` | '_ ` _ \ / _ \ \ /\ / / _ \| '__| |/ /
        | |___| | | | | | |  __/   <| | |_  |  _|| | | (_| | | | | | |  __/\ V  V / (_) | |  |   < 
        |_____|_|_| |_| |_|\___|_|\_\_|\__| |_|  |_|  \__,_|_| |_| |_|\___| \_/\_/ \___/|_|  |_|\_\
                                                                                                    
from project Abie
    - Every code I write falls under "project Abie"

            13 September, 2023 08:43 AM (Wednesday)

The project is going pretty great. Haven't yet released it, nor developed
a project creation script, nor how the virtual env shall work.

            24 October, 2023 14:12 PM (Tuesday)

I now have the virtual env up and running and able to execute a project creation file
through a batch script; the creation script is half-baked (only able to run a project, nothing else)

            18 December, 2023 6:32 AM (Monday)

The virtual env idea was a total disaster, I had to "reinvent" my code to make it work
"""

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


"""
  _     _                _    _ _     _____             _            
 | |   (_)_ __ ___   ___| | _(_) |_  | ____|_ __   __ _(_)_ __   ___ 
 | |   | | '_ ` _ \ / _ \ |/ / | __| |  _| | '_ \ / _` | | '_ \ / _ \
 | |___| | | | | | |  __/   <| | |_  | |___| | | | (_| | | | | |  __/
 |_____|_|_| |_| |_|\___|_|\_\_|\__| |_____|_| |_|\__, |_|_| |_|\___|
                                                  |___/              

This is where all the magic happens. The Engine is the core of the framework, 
as it is responsible for executing the lua code, and pretty much everything else.
"""


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
                        print(f"Error: File '{file_path}' not found.")
                        return
                    except Exception as e:
                        print(f"Error reading file: {e}")
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
        # vital_files = [
        #     "limekit.framework.scripts.limekit",
        # ]

        # for vital_file in vital_files:
        #     clean_path_file = Path.join_paths(
        #         Path.remove_last_dir(settings.limekit_SITEPACKAGE_DIR),
        #         f"{Path.dot_path(vital_file)}.lua",
        #     )

        # -----------------------------------------------------------------------
        # -----------------------------------------------------------------------
        # -----------------------------------------------------------------------
        # -----------------------------------------------------------------------

        #
        # the file with the "app" table
        # for some reason, reading from a file caused alot of errors, and the workaround it
        # was to duplicate the limekit.lua file content into some variable

        limekit_lua_file = Path.join_paths(self.limekit_root_dir, "lua", "limekit.lua")

        limekit_file_content = File.read_file(limekit_lua_file)

        # print(limekit_file_content)

        # print(File.read_file(p))

        # limekit_file_content = Script.read_app_lua()
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
            print("EntryPointError: No main.lua file found ")
            destroy_engine()

    # The PySide6 engine that handles the mainloop of the program
    def set_eventloop(self):
        self.app.execute()

    def set_custom_lua_require_path(self):
        """
        Sets custom Lua require paths by reading from a '.require' file in the project directory.
        Adds all specified directories plus the misc directory to Lua's package.path.

        Features:
        - Works across all operating systems (Windows, macOS, Linux)
        - Handles both forward and backward slashes in input paths
        - Properly formats paths for Lua's package.path
        - Supports both semicolon and newline separated paths in .require file
        - Adds paths in a cross-platform way that Lua will understand

        The .require file format can be:
        C:/dir1/dir2;D:/dir1
        or
        C:\dir1\dir2
        D:\dir1
        or any mix of separators
        """

        # Define the path to the .require file
        req_file_path = os.path.join(Path.project_path, ".require")

        # Initialize list to store all paths we'll add to package.path
        lua_path_entries = []

        # Process .require file if it exists
        if Path.check_path(req_file_path):
            try:
                # Read the file content
                require_content = File.read_file(req_file_path)

                # Split paths by either semicolon or newline, and filter out empty entries
                raw_paths = []
                if ";" in require_content:
                    raw_paths = [
                        p.strip() for p in require_content.split(";") if p.strip()
                    ]
                else:
                    raw_paths = [
                        p.strip() for p in require_content.split("\n") if p.strip()
                    ]

                # Process each path to ensure proper formatting
                for path in raw_paths:
                    # Normalize the path to use forward slashes (works on all platforms in Lua)
                    normalized_path = path.replace("\\", "/")
                    # Remove any trailing slash to standardize
                    normalized_path = normalized_path.rstrip("/")
                    # Add the ?.lua suffix (Lua's require pattern)
                    lua_path_entries.append(f"{normalized_path}/?.lua")

            except Exception as e:
                print(f"Warning: Failed to process .require file: {e}")

        # Always add the misc directory
        misc_path = os.path.normpath(Path.misc_dir()).replace("\\", "/").rstrip("/")
        scripts_path = (
            os.path.normpath(Path.scripts_dir()).replace("\\", "/").rstrip("/")
        )
        lua_path_entries.append(f"{misc_path}/?.lua")
        lua_path_entries.append(f"{scripts_path}/?.lua")

        # Combine all paths into a single string for Lua
        if lua_path_entries:
            # Join all paths with semicolons (Lua's path separator)
            paths_string = ";".join(lua_path_entries) + ";"

            # Prepend these paths to Lua's existing package.path
            # Using format() instead of f-string for broader Python version compatibility
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
        walked_classes = []  # holds all the classes found in the dir to be executed

        for app in settings.INSTALLED_PARTS:
            app_path = Path.dot_path(app)
            limekit_dir = Path.get_parent_dir(settings.limekit_SITEPACKAGE_DIR)
            full_path = os.path.join(limekit_dir, app_path)

            files_obtained = Path.walk_dir_get_files(full_path)
            walked_classes += files_obtained

        self.load_classes(walked_classes)

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
