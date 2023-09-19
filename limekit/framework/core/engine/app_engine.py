"""
            20 March, 2023 8:23 AM (Monday) (UTC+02:00)

The code is a mess, I know.... get over it... or simply fix it ;-)

            27 July, 2023 16:04 (or 4:04 PM) (Thursday) (UTC+02:00)

- Hihi! Had to fix my own mess. No more thousand imports.

            13 September, 2023 08:43 AM (Wednesday)

The project is going pretty great. Haven't yet released it yet. nor developed
a project creation script, nor how the virtual env shall work.

"""

import os
import sys
import importlib
import sqlite3
from xlsxwriter import Workbook

from playsound import playsound

from lupa import lua54
from lupa import LuaRuntime
from faker import Faker
import requests

from limekit.framework.core.config import settings
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.handle.scripts.swissknife.converters import Converter
from limekit.framework.core.runner.app import App
from limekit.framework.handle.paths.path import Path
from limekit.framework.handle.system.file import File
from limekit.framework.handle.scripts.swissknife.fileutils import FileUtils

from limekit.framework.core.exceptions.routes import RouteException

from qfluentwidgets import FluentIcon
from limekit.framework.handle.routing.routes import Routing


class Engine:
    _instance = None

    # For whatever or whoever's reason, dare not have two engine instances running
    # Here's your singleton design pattern
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.engine = None
        return cls._instance

    def __init__(self):
        self.projects_dir = Path.projects_dir()

        self.app = App()  # holds the PySide6 application
        self.routing = Routing()
        # self.plugin_manager = PluginManager()  # The code that init all user plugins

        self.limekit_root_dir = settings.limekit_SITEPACKAGE_DIR

        self.engine = None  # holds the lua engine

    # Init the JavaScript engine
    def init_lua_engine(self):
        self.engine = LuaRuntime(unpack_returned_tuples=False)

    def start(self):
        self.fix_vital_dirs()
        # self.init_plugins()  # Has to load first coz we don't walk the engine to run with only our py objects

        self.init_lua_engine()  # Set the py objects to the engine
        self.gather_lua_engine_objects()  # loads all required classes from INSTALLED_APPS and additional method
        self.set_custom_lua_require_path()

        self.init_routing_system()

        self.execute_vital_lua()  # Execute limekit.lua to enable app access
        self.execute_main_lua()  # execute user entry point file
        self.set_eventloop()  # Set the PySide6 mainloop running. VITAL!!!!!!

    def init_routing_system(self):
        project_file = Path.project_file()
        project_file_json = FileUtils.read_file_json(project_file)

        self.routing.set_project_json(project_file_json)

    # All core lua code for the limekit framework
    def execute_vital_lua(self):
        vital_files = [
            "limekit.framework.scripts.limekit",
        ]

        for vital_file in vital_files:
            clean_path_file = Path.join_paths(
                Path.remove_last_dir(settings.limekit_SITEPACKAGE_DIR),
                f"{Path.dot_path(vital_file)}.lua",
            )
            self.execute(File.read_file(clean_path_file))

    """
    For executing any incoming JavaScript code
    
    Has to redesigned to determine whether or not the framework is being run after freeze or in "IDE"
    """

    def execute(self, lua_content):
        try:
            return self.engine.execute(lua_content)
        except TypeError as exception:
            excep_msg = str(exception)

            if "takes exactly one argument" in excep_msg:
                end = excep_msg.index("()") + 2

                exce_ = str(excep_msg)[:end]
                print(
                    f"NativeMethodError: Use of 'syntactic sugar' on {exce_.replace('.',':')}. Use {exce_} instead."
                )
            else:
                print(exception)

            self.destroy_engine()

        except lua54.LuaSyntaxError as exception:
            print(exception)
            self.destroy_engine()

        except lua54.LuaError as exception:
            print(exception)

            self.destroy_engine()

        except RouteException as exception:
            print(exception)

            self.destroy_engine()

        except AttributeError as exception:
            print(exception)

            self.destroy_engine()

    # Kill the engine if anything goes wrong
    def destroy_engine(self):
        sys.exit()

    def eval(self, script):
        return self.engine.eval(script)

    # The user's main.lua entry point code
    def execute_main_lua(self):
        path_to_main = Path.scripts("main.lua")
        self.execute(File.read_file(path_to_main))

    # The PySide6 engine that handles the mainloop of the program
    def set_eventloop(self):
        self.app.execute()

    def set_custom_lua_require_path(self):
        """
        This method looks for a ".require" file in user projects dir and sets the paths in lua's
        global package.path

        Add a trailing ?.lua to each path during iteration
        """

        require_file = File.read_file(os.path.join(self.projects_dir, ".require"))
        dirs_for_require = (
            require_file.split(";") if ";" in require_file else require_file.split("\n")
        )

        paths = ""

        for dir in dirs_for_require:
            if dir != "":
                proper_path = f"{os.path.join(dir,'')}?.lua;"
                paths += proper_path

        fix_slash = paths.replace("\\", "/")
        self.execute(f"package.path = '{fix_slash}' .. package.path")

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

    def gather_lua_engine_objects(self):
        self.gather_from_dirs()
        self.gather_additional_parts()

    def gather_from_dirs(self):
        """
        Walks through all dirs desribed in settings.py INSTALLED_PARTS
        """
        walked_classes = []
        for app in settings.INSTALLED_PARTS:
            app_path = Path.dot_path(app)
            limekit_dir = Path.remove_last_dir(settings.limekit_SITEPACKAGE_DIR)
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
            "__lua_execute": self.execute_from_file,
            "sqlite3": sqlite3,
            "fake": Faker(),
            "Workbook": Workbook,
            "route": self.routing.fetch_resource,
            "Sound": playsound,
            "requests": requests,
            "py_params": Converter.py_kwargs,
            "py_indexing": Converter.py_indexing,
            "len": len,
            "dir": dir,
            "print": print,
            # --------- Data types
            "str": str,
            "dict": dict,
            "int": int,
            "tuple": tuple,
            "list": self.list_,
            "zip": self.zip_,
            # Data types ---------
            "eval": eval,
            "FluentIcon": FluentIcon,
        }

        for obj_name, object_ in other_parts.items():
            self.engine.globals()[obj_name] = object_

    def execute_from_file(self, file):
        self.execute(File.read_file(file))

    # redefining some of the in-built python methods

    """
            Using zip() method in lua
            
    names = {'John', 'Mary', 'Martha', 'James'}
    grades = {10, 80, 100, 56}
    col = zip(names, grades)
    output: [('John', 10), ('Mary', 80), ('Martha', 100), ('James', 56)]
    
    and when one passes to dict(), it returns {'John': 10, 'Mary': 80, 'Martha': 100, 'James': 56}
    """

    # The crazy thing about list() is that, when you use it on lua table, and try to access the
    # elements in lua is that, the indexing starts at 0, same as python. Python's indexing takes dominance
    # over lua's indexing (which starts at 1)
    # is dmonita
    def list_(self, list_items):
        ret_list = []
        for a in range(len(list_items)):
            ret_list.append(list_items[a + 1])  # + 1 coz lua indexes at 1

        return ret_list

    def zip_(self, arg1, arg2):
        return list(zip(self.list_(arg1), self.list_(arg2)))

    def load_classes(self, files):
        # all_instances = {}
        for file in files:
            module_name = file[:-3]

            spec = importlib.util.spec_from_file_location(module_name, file)
            module = importlib.util.module_from_spec(spec)

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

                    # Create the lua objects
                    self.engine.globals()[object_name] = class_for_lua

    def fix_vital_dirs(self):
        """
        repairs and non existing dirs in user dir; plugins, images
        """

        if not Path.check_path(Path.scripts_dir()):
            os.mkdir(Path.scripts_dir())

        if not Path.check_path(Path.misc_dir()):
            os.mkdir(Path.misc_dir())

        if not Path.check_path(Path.images_dir()):
            os.mkdir(Path.images_dir())
