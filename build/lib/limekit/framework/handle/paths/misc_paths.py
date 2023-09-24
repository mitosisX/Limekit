import os
from js2py import base

import limekit  # importing like this to get the root folder of the module


class Paths:
    project_path = os.getcwd()  # Static for easy access in multiple locations

    # The path to the user's project scripts dir
    @classmethod
    def scripts(cls, resource):
        return cls.path_res_joiner("js", resource)

    # The path to the user's project images dir
    @classmethod
    def images(cls, resource):
        return cls.path_res_joiner("images", resource)

    # The path to the user's project plugins dir
    @classmethod
    def plugins(cls):
        return cls.path_res_joiner(Paths.project_path, "plugins")

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
