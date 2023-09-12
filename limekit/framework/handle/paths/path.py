import os
import fnmatch
import limekit
from js2py import base
from limekit.framework.core.engine.parts import EnginePart
import os


class Path(EnginePart):
    project_path = os.getcwd()
    name = "__Path"

    @classmethod
    def scripts_dir(cls):
        return cls.join_paths(cls.user_project_dir(), "scripts")

    @classmethod
    def plugins_dir(cls):
        return cls.join_paths(cls.user_project_dir(), "plugins")

    @classmethod
    def misc_dir(cls):
        return cls.join_paths(cls.user_project_dir(), "misc")

    @classmethod
    def images_dir(cls):
        return cls.join_paths(cls.user_project_dir(), "images")

    @classmethod
    def user_project_dir(cls):
        return cls.project_path

    @classmethod
    def listDir(cls, path):
        return os.listdir(path)

    @classmethod
    def walk_dir_get_files(cls, dir, ext=".py"):
        python_files = []

        # Recursively iterate through the folder and its subdirectories
        for root, dirs, files in os.walk(dir):
            for filename in fnmatch.filter(
                files, f"*{ext}"
            ):  # ext should always start with a .
                if filename == "__init__.py":
                    continue
                python_files.append(os.path.join(root, filename))

        return python_files

    # a method that removes the last dir of any given path
    @classmethod
    def remove_last_dir(cls, path):
        # Step 1: Split the path into individual directories
        directories = path.split("\\")

        # Step 2: Remove the last directory
        directories = directories[:-1]

        # Step 3: Join the directories back together to form the new path
        new_path = "\\".join(directories)

        return new_path

    # Create an OS dependent path from any given string
    @classmethod
    def join_paths(cls, *path):
        return os.path.join(*path)

    # The path to the user's project scripts dir
    @classmethod
    def scripts(cls, resource):
        return cls.path_res_joiner("scripts", resource)

    # The path to the user's project images dir
    @classmethod
    def images(cls, resource):
        return cls.path_res_joiner("images", resource)

    # The path to the user's project images dir
    @classmethod
    def misc(cls, resource):
        return cls.path_res_joiner("misc", resource)

    # The path to the user's project plugins dir
    @classmethod
    def plugins(cls):
        return cls.path_res_joiner(cls.project_path, "plugins")

    # The path to the installed limekit module
    @classmethod
    def limekit_sitepackage_path(cls):
        return limekit.__path__[0]  # limekit path in site-packages

    # When the below method is called from JS, the arguments no longer get treated
    # as a string, rather some js2py type, and that's the whole reason the conditional initialization
    @classmethod
    def path_res_joiner(cls, path, resource):
        return os.path.join(
            cls.project_path,
            path,
            resource.to_string().value
            if type(resource) == base.PyJsString
            else resource,
        )

    @classmethod
    def dot_path(cls, dot_path):
        """
        Converts a path string with dot notation into a proper path.
        For example, converts "my.folder.name" to "my/folder/name".
        """
        return dot_path.replace(".", "/")

    @classmethod
    def check_path(cls, path):
        return True if os.path.exists(path) else False
