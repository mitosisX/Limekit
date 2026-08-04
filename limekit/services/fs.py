"""File-system access for Lua: everything under `require("limekit.fs")`.

Ports limekit/utils/file.py and limekit/utils/fileutils.py (1.x) to the 2.0
service-layer pattern. Every failure crossing the bridge becomes a
BridgeError -- 1.x let raw OSError/ValueError/JSONDecodeError reach Lua as
opaque userdata, which lupa cannot present usefully to a Lua script.
"""

import json
import os
import shutil

from limekit.kernel.bridge.convert import to_lua
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError


def _path(value, label="path"):
    if not isinstance(value, str) or not value:
        raise BridgeError(f"expected a non-empty string for {label}, got {value!r}")
    return value


class FileSystem(LimeObject):
    __lime__ = "fs.FileSystem"

    # -- reading / writing --------------------------------------------------

    @staticmethod
    def readFile(path, encoding="utf-8"):
        path = _path(path)
        try:
            with open(path, "r", encoding=encoding) as fh:
                return fh.read()
        except (OSError, LookupError, UnicodeDecodeError) as exc:
            raise BridgeError(f"could not read {path!r}: {exc}") from exc

    @staticmethod
    def writeFile(path, content, encoding="utf-8"):
        path = _path(path)
        if not isinstance(content, str):
            raise BridgeError(f"expected string content, got {content!r}")
        try:
            with open(path, "w", encoding=encoding) as fh:
                fh.write(content)
        except (OSError, LookupError) as exc:
            raise BridgeError(f"could not write {path!r}: {exc}") from exc
        return True

    @staticmethod
    def appendFile(path, content, encoding="utf-8"):
        path = _path(path)
        if not isinstance(content, str):
            raise BridgeError(f"expected string content, got {content!r}")
        try:
            with open(path, "a", encoding=encoding) as fh:
                fh.write(content)
        except (OSError, LookupError) as exc:
            raise BridgeError(f"could not append to {path!r}: {exc}") from exc
        return True

    @staticmethod
    def createFile(path):
        path = _path(path)
        try:
            with open(path, "x", encoding="utf-8"):
                pass
        except OSError as exc:
            raise BridgeError(f"could not create {path!r}: {exc}") from exc
        return True

    @staticmethod
    def deleteFile(path):
        path = _path(path)
        try:
            os.remove(path)
        except OSError as exc:
            raise BridgeError(f"could not delete {path!r}: {exc}") from exc
        return True

    @staticmethod
    def copyFile(source, destination):
        source = _path(source, "source")
        destination = _path(destination, "destination")
        try:
            shutil.copyfile(source, destination)
        except OSError as exc:
            raise BridgeError(
                f"could not copy {source!r} to {destination!r}: {exc}"
            ) from exc
        return True

    @staticmethod
    def renameFile(path, new_path):
        path = _path(path)
        new_path = _path(new_path, "new_path")
        try:
            os.rename(path, new_path)
        except OSError as exc:
            raise BridgeError(
                f"could not rename {path!r} to {new_path!r}: {exc}"
            ) from exc
        return True

    # -- queries --------------------------------------------------------

    @staticmethod
    def exists(path):
        return os.path.exists(_path(path))

    @staticmethod
    def isFolder(path):
        return os.path.isdir(_path(path))

    @staticmethod
    def isFileEmpty(path):
        path = _path(path)
        if not os.path.isfile(path):
            raise BridgeError(f"no such file: {path!r}")
        try:
            return os.path.getsize(path) == 0
        except OSError as exc:
            raise BridgeError(f"could not stat {path!r}: {exc}") from exc

    @staticmethod
    def getFileName(path):
        return os.path.basename(_path(path))

    @staticmethod
    def getFileSize(path):
        path = _path(path)
        try:
            return os.path.getsize(path)
        except OSError as exc:
            raise BridgeError(f"could not stat {path!r}: {exc}") from exc

    @staticmethod
    def getFileExt(path):
        return os.path.splitext(_path(path))[1]

    # -- directories ------------------------------------------------------

    @staticmethod
    def createFolder(path):
        path = _path(path)
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as exc:
            raise BridgeError(f"could not create folder {path!r}: {exc}") from exc
        return True

    @staticmethod
    def listFolder(path):
        path = _path(path)
        try:
            entries = sorted(os.listdir(path), key=str.lower)
        except OSError as exc:
            raise BridgeError(f"could not list {path!r}: {exc}") from exc
        return to_lua(entries)

    @staticmethod
    def walkDir(path, show_hidden=False):
        path = _path(path)
        if not os.path.isdir(path):
            raise BridgeError(f"no such directory: {path!r}")

        dirs, files = [], []
        try:
            with os.scandir(path) as it:
                for entry in it:
                    if not show_hidden and entry.name.startswith("."):
                        continue
                    data = {
                        "name": entry.name,
                        "path": entry.path,
                        "is_dir": entry.is_dir(),
                    }
                    (dirs if entry.is_dir() else files).append(data)
        except OSError as exc:
            raise BridgeError(f"could not walk {path!r}: {exc}") from exc

        dirs.sort(key=lambda item: item["name"].lower())
        files.sort(key=lambda item: item["name"].lower())
        return to_lua(dirs + files)

    # -- paths --------------------------------------------------------------

    @staticmethod
    def joinPaths(*parts):
        if not parts:
            raise BridgeError("joinPaths requires at least one path segment")
        for part in parts:
            if not isinstance(part, str):
                raise BridgeError(f"expected string path segments, got {part!r}")
        return os.path.normpath(os.path.join(*parts))

    @staticmethod
    def normalPath(path):
        return os.path.normpath(_path(path))

    @staticmethod
    def getDirName(path):
        return os.path.dirname(_path(path))

    # -- JSON -----------------------------------------------------------

    @staticmethod
    def readJSON(path):
        path = _path(path)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            raise BridgeError(f"could not read JSON from {path!r}: {exc}") from exc
        return to_lua(data)

    @staticmethod
    def writeJSON(path, data, indent=4):
        from limekit.kernel.bridge.convert import to_py
        path = _path(path)
        try:
            payload = to_py(data)
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=indent)
        except (OSError, TypeError, ValueError) as exc:
            raise BridgeError(f"could not write JSON to {path!r}: {exc}") from exc
        return True

    @staticmethod
    def formatJSON(text, indent=4):
        if not isinstance(text, str):
            raise BridgeError(f"expected a JSON string, got {text!r}")
        try:
            data = json.loads(text)
            return json.dumps(data, indent=indent)
        except json.JSONDecodeError as exc:
            raise BridgeError(f"malformed JSON: {exc}") from exc

    @staticmethod
    def readFileLines(path, encoding="utf-8"):
        path = _path(path)
        try:
            with open(path, "r", encoding=encoding) as fh:
                lines = fh.read().splitlines()
        except (OSError, LookupError, UnicodeDecodeError) as exc:
            raise BridgeError(f"could not read {path!r}: {exc}") from exc
        return to_lua(lines)
