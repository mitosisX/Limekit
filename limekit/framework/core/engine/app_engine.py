"""
from project Abigail
    - Every code I write falls under "project Abigail"

            13 September, 2023 08:43 AM (Wednesday)

The project is going pretty great. Haven't yet released it. nor developed
a project creation script, nor how the virtual env shall work.

            24 October, 2023 14:12 PM (Tuesday)
            
I now have the virtual env up and running and able to execute a project creation py file 
through a batch script; the creation script is half-baked (only able to run a project, nothing else)

            18 December, 2023 6:32 AM (Monday)
            
The virt env idea was a total disaster, I had to reinvent my code to make it work
"""

import os
import sys
import inspect
import importlib

# from xlsxwriter import Workbook

from playsound import playsound

import lupa
from lupa import LuaRuntime

# from faker import Faker

from limekit.framework.core.config import settings
from limekit.framework.core.engine.parts import EnginePart

# Was experiencing circular import in Converter, thats why I am separating the engine for global use
from limekit.framework.core.engine.global_ import GlobalEngine
from limekit.framework.handle.scripts.swissknife.converters import Converter
from limekit.framework.core.runner.app import App

from limekit.framework.handle.paths.path import Path
from limekit.framework.handle.system.file import File
from limekit.framework.handle.scripts.swissknife.fileutils import FileUtils

from limekit.framework.handle.routing.routes import Routing
from limekit.framework.core.runner.app_events import AppEvents

from limekit.framework.scripts.script import Script


class Engine:
    # _instance = None

    # For whatever or whoever's reason, dare not have two engine instances running
    # Here's your singleton design pattern
    # def __new__(cls):
    #     if cls._instance is None:
    #         cls._instance = super().__new__(cls)
    #         cls._instance.engine = None
    #     return cls._instance

    def __init__(self):
        self.projects_dir = Path.projects_dir()

        self.app = App()  # holds the PySide6 QApplication
        self.app_events = AppEvents()
        self.routing = Routing()
        # self.plugin_manager = PluginManager()  # The code that init all user plugins

        self.limekit_root_dir = settings.limekit_SITEPACKAGE_DIR

        self.engine = None  # holds the lua engine

    # These shall serve as property access constraints
    def _getter_restric(self, obj, attr_name):
        if attr_name != "name":
            return getattr(obj, attr_name)

    def _setter_restric(self, obj, attr_name, value):
        if attr_name != "put":
            setattr(obj, attr_name, value)
            return

    # Init the JavaScript engine
    def init_lua_engine(self):
        self.engine = LuaRuntime(
            unpack_returned_tuples=True,
            # attribute_handlers=(self._getter_restric, self._setter_restric),
        )
        GlobalEngine.global_engine = self.engine

    def start(self):
        # self.fix_vital_dirs() # Unnecessary, handled by the runner and the future build engine
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

        # for vital_file in vital_files:
        #     clean_path_file = Path.join_paths(
        #         Path.remove_last_dir(settings.limekit_SITEPACKAGE_DIR),
        #         f"{Path.dot_path(vital_file)}.lua",
        #     )

        self.execute(Script.read_app_lua())

    """
    For executing any incoming JavaScript code
    
    Has to redesigned to determine whether or not the framework is being run after freeze or in "IDE"
    """

    def execute(self, lua_content):
        self.engine.execute(lua_content)

    def evaluate(self, content):
        return self.engine.eval(content)

    # Kill the engine if anything goes wrong

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

        Structure: C:/dir1/dir2;D:/dir1; or sep by \n D:/lua;D:/Misc;
        """

        req_file_path = os.path.join(Path.project_path, ".require")

        dirs_for_require = []  # Where

        if Path.check_path(req_file_path):
            require_file = File.read_file(req_file_path)
            dirs_for_require = (
                require_file.split(";")[:-1]
                if ";" in require_file
                else require_file.split("\n")[:-1]
            )

            misc_path_append = Path.misc_dir().replace(
                "\\", "/"
            )  # make sure all scripts in the misc can be "require"-d

            dirs_for_require.append(misc_path_append)

            paths = ""

            for dir in dirs_for_require:
                if dir != "":
                    # proper_path = f"{dir}{'/' if not dir.endswith('/') else ''}?.lua;"
                    proper_path = "%s%s?.lua;" % (
                        dir,
                        "/" if not dir.endswith("/") else "",
                    )
                    paths += proper_path

            # fix_slash = paths.replace("\\", "/")

            # self.execute(f"package.path = '{paths}' .. package.path")
            self.execute("package.path = '" + paths + "' .. package.path")
        else:
            misc_path_append = Path.misc_dir().replace("\\", "/") + "/?.lua"

            # self.execute(f"package.path = '{misc_path_append};' .. package.path")
            self.execute("package.path = '" + misc_path_append + ";' .. package.path")

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

    def execute_from_file(self, file):
        self.execute(File.read_file(file))

    def __quit(self):
        self.app.app.instance().quit()

    """
    # Lupa sometimes wraps python object or return them as is.
    
    - IndexError may sometimes be raised when trying to access some attributes.
    - The way around this is to pass the object to 
    
    site = requests.get('https://webscraper.io/test-sites/e-commerce/allinone')
    soup = BeautifulSoup(site.text, "html.parser")
    local divs = py_getatrr(soup).findAll('div','col-sm-4 col-lg-4 col-md-4')
    
    - This method works wonders.
    
    PS. Haven't yet met anything requiring py_getitem yet
    """

    def load_classes(self, files):
        for file in files:
            if True:
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

                        # Create the lua objects
                        self.engine.globals()[object_name] = class_for_lua

    def load_classes_(self, files):
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

    """
    def fix_vital_dirs(self):
        if not Path.check_path(Path.scripts_dir()):
            os.mkdir(Path.scripts_dir())

        if not Path.check_path(Path.misc_dir()):
            os.mkdir(Path.misc_dir())

        if not Path.check_path(Path.images_dir()):
            os.mkdir(Path.images_dir())     
    """


# 24 December, 2023 17:02 PM (Sunday)
class Build:
    # data refers to the limey props: name, version...
    def __init__(self, data=None):
        pass

    def copy_vital_dirs(self):
        pass

    def create_build_files_and_folders(self):
        pass
