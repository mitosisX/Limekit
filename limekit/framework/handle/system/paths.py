import os
from PySide6.QtCore import QStandardPaths
from limekit.framework.core.engine.parts import EnginePart


class Paths(EnginePart):
    name = "__paths"

    paths = {
        "desktop": QStandardPaths.StandardLocation.DesktopLocation,
        "documents": QStandardPaths.StandardLocation.DocumentsLocation,
        "fonts": QStandardPaths.StandardLocation.FontsLocation,
        "applications": QStandardPaths.StandardLocation.ApplicationsLocation,
        "music": QStandardPaths.StandardLocation.MusicLocation,
        "movies": QStandardPaths.StandardLocation.MoviesLocation,
        "pictures": QStandardPaths.StandardLocation.PicturesLocation,
        "temp": QStandardPaths.StandardLocation.TempLocation,
        "home": QStandardPaths.StandardLocation.HomeLocation,
        "applocaldata": QStandardPaths.StandardLocation.AppLocalDataLocation,
        "cache": QStandardPaths.StandardLocation.CacheLocation,
        "genericdata": QStandardPaths.StandardLocation.GenericDataLocation,
        "runtime": QStandardPaths.StandardLocation.RuntimeLocation,
        "config": QStandardPaths.StandardLocation.ConfigLocation,
        "download": QStandardPaths.StandardLocation.DownloadLocation,
        "genericcache": QStandardPaths.StandardLocation.GenericCacheLocation,
        "genericconfig": QStandardPaths.StandardLocation.GenericConfigLocation,
        "appdata": QStandardPaths.StandardLocation.AppDataLocation,
        "appconfig": QStandardPaths.StandardLocation.AppConfigLocation,
        "publicshare": QStandardPaths.StandardLocation.PublicShareLocation,
        "templates": QStandardPaths.StandardLocation.TemplatesLocation,
    }

    @classmethod
    def get_path(cls, path):
        check_path = cls.paths.get(path)
        if check_path:
            the_path = QStandardPaths.writableLocation(check_path)
            return the_path
        return "Blank"

    @staticmethod
    def join_paths(*paths):
        return os.path.join(*paths)
