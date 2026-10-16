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
from limekit.kernel.spec import method


def _path(value, label="path"):
    if not isinstance(value, str) or not value:
        raise BridgeError(f"expected a non-empty string for {label}, got {value!r}")
    return value


# One provider for the process: it caches icons per file type.
_icon_provider = None
_image_suffixes = None


class FileSystem(LimeObject):
    __lime__ = "fs.FileSystem"

    # -- reading / writing --------------------------------------------------

    @staticmethod
    @method({"path": "string", "encoding": "string"}, returns="string", doc="The whole file as a string.")
    def readFile(path, encoding="utf-8"):
        path = _path(path)
        try:
            with open(path, "r", encoding=encoding) as fh:
                return fh.read()
        except (OSError, LookupError, UnicodeDecodeError) as exc:
            raise BridgeError(f"could not read {path!r}: {exc}") from exc

    @staticmethod
    @method({"path": "string", "data": "string"},
            doc="Writes binary content given as base64 text -- the way to write "
                "an image, or any bytes, from Lua: a Lua string crosses the "
                "bridge as text, so raw bytes cannot be passed as one.")
    def writeBase64(path, data):
        import base64
        import binascii
        path = _path(path)
        try:
            payload = base64.b64decode(str(data), validate=True)
        except (binascii.Error, ValueError) as exc:
            raise BridgeError(f"not valid base64: {exc}") from exc
        try:
            with open(path, "wb") as fh:
                fh.write(payload)
        except OSError as exc:
            raise BridgeError(f"could not write {path!r}: {exc}") from exc
        return True

    @staticmethod
    @method({"path": "string"}, returns="string",
            doc="A file's bytes as base64 text; the counterpart of writeBase64.")
    def readBase64(path):
        import base64
        path = _path(path)
        try:
            with open(path, "rb") as fh:
                return base64.b64encode(fh.read()).decode("ascii")
        except OSError as exc:
            raise BridgeError(f"could not read {path!r}: {exc}") from exc

    @staticmethod
    @method({"path": "string", "content": "string", "encoding": "string"}, doc="Writes content, replacing whatever was there.")
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
    @method({"path": "string", "content": "string", "encoding": "string"}, doc="Adds content to the end of the file.")
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
    @method({"path": "string"}, doc="Creates an empty file.")
    def createFile(path):
        path = _path(path)
        try:
            with open(path, "x", encoding="utf-8"):
                pass
        except OSError as exc:
            raise BridgeError(f"could not create {path!r}: {exc}") from exc
        return True

    @staticmethod
    @method({"path": "string"}, doc="Deletes a file.")
    def deleteFile(path):
        path = _path(path)
        try:
            os.remove(path)
        except OSError as exc:
            raise BridgeError(f"could not delete {path!r}: {exc}") from exc
        return True

    @staticmethod
    @method({"source": "string", "destination": "string"}, doc="Copies a file.")
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
    @method({"path": "string", "new_path": "string"}, doc="Renames or moves a file.")
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
    @method({"path": "string"}, returns="boolean", doc="Whether a file or folder exists.")
    def exists(path):
        return os.path.exists(_path(path))

    @staticmethod
    @method({"path": "string"}, returns="boolean", doc="Whether the path is a folder.")
    def isFolder(path):
        return os.path.isdir(_path(path))

    @staticmethod
    @method({"path": "string"}, returns="boolean", doc="Whether the file has no content.")
    def isFileEmpty(path):
        path = _path(path)
        if not os.path.isfile(path):
            raise BridgeError(f"no such file: {path!r}")
        try:
            return os.path.getsize(path) == 0
        except OSError as exc:
            raise BridgeError(f"could not stat {path!r}: {exc}") from exc

    @staticmethod
    @method({"path": "string"}, returns="string", doc="The filename portion of a path.")
    def getFileName(path):
        return os.path.basename(_path(path))

    @staticmethod
    @method({"path": "string"}, returns="integer", doc="Size in bytes.")
    def getFileSize(path):
        path = _path(path)
        try:
            return os.path.getsize(path)
        except OSError as exc:
            raise BridgeError(f"could not stat {path!r}: {exc}") from exc

    @staticmethod
    @method({"path": "string"}, returns="string", doc="The file extension.")
    def getFileExt(path):
        return os.path.splitext(_path(path))[1]

    # -- directories ------------------------------------------------------

    @staticmethod
    @method({"path": "string"}, doc="Creates a folder, including any missing parents.")
    def createFolder(path):
        path = _path(path)
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as exc:
            raise BridgeError(f"could not create folder {path!r}: {exc}") from exc
        return True

    @staticmethod
    @method({"path": "string"}, returns="string[]", doc="The names directly inside a folder.")
    def listFolder(path):
        path = _path(path)
        try:
            entries = sorted(os.listdir(path), key=str.lower)
        except OSError as exc:
            raise BridgeError(f"could not list {path!r}: {exc}") from exc
        return to_lua(entries)

    @staticmethod
    @method({"path": "string", "show_hidden": "boolean"},
            returns="table[]",
            doc="One level of a folder, folders first. Each entry is a table "
                "with name, path and is_dir. Not recursive, despite the name -- "
                "call it again on any entry whose is_dir is true.")
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

    # -- icons --------------------------------------------------------------

    @staticmethod
    @method({"path": "string"}, returns="any",
            doc="The icon the operating system shows for this file or folder, "
                "for setIcon. An image file shows a small picture of itself.")
    def getFileIcon(path):
        """The desktop's own icon for a path -- Explorer's on Windows,
        Finder's on macOS, the icon theme's on Linux -- so a file list looks
        like every other file list on the machine and nobody assigns icons
        by hand. Images are the exception: a thumbnail of the picture says
        more than the generic "image" icon does.
        """
        from PySide6.QtCore import QFileInfo
        from PySide6.QtGui import QIcon, QImageReader
        from PySide6.QtWidgets import QFileIconProvider

        path = _path(path)
        if os.path.isfile(path):
            suffix = os.path.splitext(path)[1].lower().lstrip(".")
            global _image_suffixes
            if _image_suffixes is None:
                _image_suffixes = {bytes(f).decode() for f in QImageReader.supportedImageFormats()}
            # QIcon loads lazily, when the icon is first drawn; the size cap
            # keeps a huge photo from stalling the first paint of a list.
            if suffix in _image_suffixes and os.path.getsize(path) <= 4 * 1024 * 1024:
                icon = QIcon(path)
                if not icon.isNull():
                    return icon
        global _icon_provider
        if _icon_provider is None:
            _icon_provider = QFileIconProvider()
        return _icon_provider.icon(QFileInfo(path))

    # -- paths --------------------------------------------------------------

    @staticmethod
    @method(returns="string", doc="Joins path segments with the right separator for the platform.")
    def joinPaths(*parts):
        if not parts:
            raise BridgeError("joinPaths requires at least one path segment")
        for part in parts:
            if not isinstance(part, str):
                raise BridgeError(f"expected string path segments, got {part!r}")
        return os.path.normpath(os.path.join(*parts))

    @staticmethod
    @method({"path": "string"}, returns="string", doc="Normalises a path.")
    def normalPath(path):
        return os.path.normpath(_path(path))

    @staticmethod
    @method({"path": "string"}, returns="string", doc="The folder containing the path.")
    def getDirName(path):
        return os.path.dirname(_path(path))

    # -- JSON -----------------------------------------------------------

    @staticmethod
    @method({"path": "string"}, returns="table", doc="Reads a JSON file and returns it as a lua table.")
    def readJSON(path):
        path = _path(path)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            raise BridgeError(f"could not read JSON from {path!r}: {exc}") from exc
        return to_lua(data)

    @staticmethod
    @method({"path": "string", "data": "table", "indent": "integer"}, doc="Writes a lua table as JSON.")
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
    @method({"text": "string", "indent": "integer"}, returns="string", doc="Pretty-prints a JSON string without touching a file.")
    def formatJSON(text, indent=4):
        if not isinstance(text, str):
            raise BridgeError(f"expected a JSON string, got {text!r}")
        try:
            data = json.loads(text)
            return json.dumps(data, indent=indent)
        except json.JSONDecodeError as exc:
            raise BridgeError(f"malformed JSON: {exc}") from exc

    @staticmethod
    @method({"path": "string", "encoding": "string"}, returns="string[]", doc="The file as a table of lines.")
    def readFileLines(path, encoding="utf-8"):
        path = _path(path)
        try:
            with open(path, "r", encoding=encoding) as fh:
                lines = fh.read().splitlines()
        except (OSError, LookupError, UnicodeDecodeError) as exc:
            raise BridgeError(f"could not read {path!r}: {exc}") from exc
        return to_lua(lines)
