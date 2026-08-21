"""System-level utilities exposed to Lua as `require("limekit.sys").System`.

Ports limekit/utils/sysutil.py, limekit/utils/emoji_str.py and the process/
clipboard bits of 1.x's `app` table to the 2.0 service-layer pattern.
"""

import base64
import hashlib
import os
import platform
import random
import subprocess
import sys
import time

from limekit.kernel.bridge.convert import to_lua
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import method

_EXECUTE_TIMEOUT_SECONDS = 30

_HASH_ALGORITHMS = {
    "md5", "sha1", "sha224", "sha256", "sha384", "sha512",
}


class System(LimeObject):
    __lime__ = "sys.System"

    # -- processes ----------------------------------------------------------

    @staticmethod
    @method({"cmd": "string"}, returns="string", doc="Runs an external command and returns its output. Bounded at 30 seconds.")
    def execute(cmd):
        """Run a shell command and return (stdout, stderr, returncode).

        Bounded by a timeout so a hung child process cannot block the GUI
        thread forever -- 1.x's equivalent had no timeout at all.
        """
        if not isinstance(cmd, str) or not cmd:
            raise BridgeError(f"expected a non-empty command string, got {cmd!r}")
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                timeout=_EXECUTE_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            raise BridgeError(
                f"command timed out after {_EXECUTE_TIMEOUT_SECONDS}s: {cmd!r}"
            ) from exc
        except OSError as exc:
            raise BridgeError(f"could not run {cmd!r}: {exc}") from exc
        return to_lua({
            "stdout": result.stdout, "stderr": result.stderr,
            "returncode": result.returncode,
        })

    @staticmethod
    @method({"path": "string"}, returns="boolean", doc="Opens a file, folder or URL with whatever the desktop has registered for it.")
    def openPath(path):
        """Hand a path to the desktop and let it choose the application.

        `execute()` is the wrong tool for this: it is synchronous and capped
        at 30 seconds, so launching an editor would freeze the interface
        until the user closed it again. QDesktopServices returns as soon as
        the child is handed off.

        A path that exists is opened as a local file; anything else is
        treated as a URL, so both openPath("/home/me/main.lua") and
        openPath("https://limekit.dev") do the expected thing.
        """
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices

        if not isinstance(path, str) or not path:
            raise BridgeError(f"expected a non-empty path string, got {path!r}")
        if os.path.exists(path):
            url = QUrl.fromLocalFile(os.path.abspath(path))
        else:
            url = QUrl(path)
        return bool(QDesktopServices.openUrl(url))

    @staticmethod
    @method({"code": "integer"}, doc="Quits the application.")
    def exit(code=0):
        sys.exit(int(code))

    # -- system info ----------------------------------------------------

    @staticmethod
    @method(returns="string", doc="The operating system name.")
    def getOSName():
        return platform.system()

    @staticmethod
    @method(returns="string", doc="The operating system version.")
    def getOSVersion():
        return platform.version()

    @staticmethod
    @method(returns="string", doc="The platform identifier.")
    def getPlatformName():
        return platform.platform()

    @staticmethod
    @method(returns="string", doc="The CPU model name.")
    def getProcessorName():
        return platform.processor()

    @staticmethod
    @method(returns="integer", doc="How many CPU cores are available.")
    def getCPUCount():
        count = os.cpu_count()
        if count is None:
            raise BridgeError("could not determine CPU count on this platform")
        return count

    @staticmethod
    @method({"name": "string"}, returns="string", doc="A well-known folder such as desktop, documents, downloads or temp.")
    def getStandardPath(name):
        """A named QStandardPaths location, e.g. 'documents', 'home'."""
        from PySide6.QtCore import QStandardPaths
        key = f"{name.strip().title().replace(' ', '')}Location"
        location = getattr(QStandardPaths.StandardLocation, key, None)
        if location is None:
            raise BridgeError(
                f"unknown standard path {name!r}; expected one of the "
                f"QStandardPaths locations, e.g. 'documents', 'home', 'temp'"
            )
        return QStandardPaths.writableLocation(location)

    @staticmethod
    @method({"seconds": "number"}, doc="Pauses for a number of seconds. Blocks the interface -- prefer sys.Thread.")
    def sleep(seconds):
        try:
            duration = float(seconds)
        except (TypeError, ValueError) as exc:
            raise BridgeError(f"expected a number of seconds, got {seconds!r}") from exc
        if duration < 0:
            raise BridgeError(f"cannot sleep a negative duration: {duration}")
        time.sleep(duration)
        return None

    # -- clipboard --------------------------------------------------------

    @staticmethod
    @method(returns="string", doc="The text currently on the clipboard.")
    def getClipboardText():
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        if clipboard is None:
            raise BridgeError("no QApplication clipboard is available")
        return clipboard.text()

    @staticmethod
    @method({"text": "string"}, doc="Puts text on the clipboard.")
    def setClipboardText(text):
        from PySide6.QtWidgets import QApplication
        if not isinstance(text, str):
            raise BridgeError(f"expected a string, got {text!r}")
        clipboard = QApplication.clipboard()
        if clipboard is None:
            raise BridgeError("no QApplication clipboard is available")
        clipboard.setText(text)
        return True

    # -- misc ---------------------------------------------------------------

    @staticmethod
    @method({"text": "string", "sep": "string"}, returns="string[]", doc="Splits a string into a table.")
    def splitString(text, sep=" "):
        if not isinstance(text, str):
            raise BridgeError(f"expected a string, got {text!r}")
        return to_lua(text.split(sep))

    @staticmethod
    @method({"items": "any[]"}, returns="any", doc="Picks one item from a table at random.")
    def randomChoice(items):
        from limekit.kernel.bridge.convert import as_sequence
        options = as_sequence(items)
        if not options:
            raise BridgeError("randomChoice requires at least one item")
        return random.choice(options)

    @staticmethod
    @method({"name": "string"}, returns="string", doc="Looks up an emoji by name.")
    def emoji(name):
        try:
            import emoji as emoji_pkg
        except ImportError as exc:
            raise BridgeError(
                "the 'emoji' package is not installed; install it with "
                "'pip install emoji' to use sys.System.emoji"
            ) from exc
        if not isinstance(name, str):
            raise BridgeError(f"expected a string, got {name!r}")
        return emoji_pkg.emojize(name, language="alias")

    @staticmethod
    @method({"kind": "string", "text": "string"}, returns="string", doc="Hashes a string: md5, sha1, sha224, sha256, sha384 or sha512.")
    def makeHash(kind, text):
        if not isinstance(kind, str) or kind.lower() not in _HASH_ALGORITHMS:
            raise BridgeError(
                f"unknown hash algorithm {kind!r}; expected one of: "
                f"{', '.join(sorted(_HASH_ALGORITHMS))}"
            )
        if not isinstance(text, str):
            raise BridgeError(f"expected a string, got {text!r}")
        return hashlib.new(kind.lower(), text.encode("utf-8")).hexdigest()

    @staticmethod
    @method({"text": "string"}, returns="string", doc="Encodes a string as base64.")
    def toBase64(text):
        if not isinstance(text, str):
            raise BridgeError(f"expected a string, got {text!r}")
        return base64.b64encode(text.encode("utf-8")).decode("ascii")

    @staticmethod
    @method({"text": "string"}, returns="string", doc="Decodes a base64 string.")
    def fromBase64(text):
        if not isinstance(text, str):
            raise BridgeError(f"expected a string, got {text!r}")
        try:
            return base64.b64decode(text.encode("ascii")).decode("utf-8")
        except Exception as exc:                            # noqa: BLE001
            raise BridgeError(f"could not decode base64 {text!r}: {exc}") from exc

    @staticmethod
    @method({"size": "integer"}, returns="string", doc="Turns a byte count into a readable size such as 1.4 MB.")
    def bytesToReadableSize(size):
        try:
            value = float(size)
        except (TypeError, ValueError) as exc:
            raise BridgeError(f"expected a number of bytes, got {size!r}") from exc
        if value < 0:
            raise BridgeError(f"cannot format a negative size: {value}")
        for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
            if value < 1024 or unit == "PB":
                return f"{value:.2f} {unit}" if unit != "B" else f"{int(value)} {unit}"
            value /= 1024
