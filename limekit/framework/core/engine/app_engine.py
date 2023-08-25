"""
20 March, 2023 8:23 AM (Monday) (UTC+02:00)

The code is a mess, I know.... get over it... or simply fix it ;-)

27 July, 2023 16:04 (or 4:04 PM) (Thursday) (UTC+02:00)

- Hihi! Had to fix my own mess. No more thousand imports.

"""

import os
import importlib
import sqlite3

import lupa
from lupa import LuaRuntime
from faker import Faker

from limekit.framework.core.config import settings
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.core.runner.app import App
from limekit.framework.handle.paths.path import Path
from limekit.framework.handle.plugins.plugin_manager import PluginManager


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
        self.app = App()  # holds the PySide6 application
        # self.plugin_manager = PluginManager()  # The code that init all user plugins

        self.limekit_root_dir = settings.limekit_SITEPACKAGE_DIR

        self.engine = None  # holds the js2py engine

    # Init the JavaScript engine
    def init_JsEngine(self):
        self.engine = LuaRuntime(unpack_returned_tuples=True)

    def start(self):
        self.fix_vital_dirs()
        # self.init_plugins()  # Has to load first coz we don't walk the engine to run with only our py objects

        self.init_JsEngine()  # Set the py objects to the engine
        self.gather_js_engine_objects()
        self.execute_vital_lua()  # Set the py objects to the engine
        self.execute_main_lua()  # Set the py objects to the engine
        self.set_eventloop()  # Set the PySide6 mainloop running. VITAL!!!!!!

    # All core js code for the limekit framework
    def execute_vital_lua(self):
        vital_files = [
            "limekit.framework.scripts.limekit",
        ]

        for vital_file in vital_files:
            clean_path_file = Path.join_paths(
                Path.remove_last_dir(settings.limekit_SITEPACKAGE_DIR),
                f"{Path.dot_path(vital_file)}.lua",
            )
            self.execute(clean_path_file)

    """
    For executing any incoming JavaScript code
    
    Has to redesigned to determine whether or not the framework is being run after freeze or in "IDE"
    """

    def execute(self, script):
        with open(script) as js_script:
            lua_content = js_script.read()

            self.engine.execute(lua_content)

    # The user's main.js entry point code
    def execute_main_lua(self):
        path_to_main = Path.scripts("main.lua")
        self.execute(path_to_main)

    # The PySide6 engine that handles the mainloop of the program
    def set_eventloop(self):
        self.app.execute()

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

    def gather_js_engine_objects(self):
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
        Some additional functions such as using len() in js or anything required but not
        really that essential (well, some)
        """
        other_parts = {
            "scripts": Path.scripts,
            "images": Path.images,
            "__js_execute": self.execute,
            "sqlite": sqlite3,
            "fake": Faker(),
            "len": len,
            "console.log": print,
            "print": print,
            "str": str,
            "eval": eval,
        }

        for obj_name, object_ in other_parts.items():
            self.engine.globals()[obj_name] = object_

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
                    class_for_js = class_

                    object_name = (
                        class_for_js.name
                        if class_for_js.name
                        else class_for_js.__name__
                    )

                    # Create the lua objects
                    self.engine.globals()[object_name] = class_for_js

    def fix_vital_dirs(self):
        """
        repairs and non existing dirs in user dir; plugins, images
        """

        if not Path.check_path(Path.scripts_dir()):
            os.mkdir(Path.scripts_dir())

        # if not Path.check_path(Path.plugins_dir()):
        #     os.mkdir(Path.plugins_dir())

        if not Path.check_path(Path.images_dir()):
            os.mkdir(Path.images_dir())
