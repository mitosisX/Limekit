"""Watching the filesystem: `require("limekit.sys").FileWatcher`.

Qt's own watcher has three sharp edges, and anything built directly on it
inherits all of them:

* It is not recursive. Watching a project folder tells you nothing about a
  file created two folders down, so every directory has to be added by hand.
* It reports a directory change, not what changed. A file created, deleted
  or renamed all arrive as the same signal about the same folder.
* It is chatty. Saving one file in an editor commonly produces several
  events -- a temporary file appears, is renamed over the target, and the
  original is removed -- so a handler that rebuilds anything expensive runs
  three or four times for one save.

So this wraps it: `watchTree` adds every directory beneath a root, and
changes are collected for a moment before the handler is told once.
"""

import os

from PySide6.QtCore import QFileSystemWatcher, QObject, QTimer

from limekit.kernel.bridge.convert import to_lua
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import method

# Long enough to swallow an editor's save dance, short enough that a change
# still feels immediate.
_SETTLE_MSECS = 250

# A directory count past which watching stops being sensible: every entry
# costs an OS handle, and a project that reaches this is one somebody has
# pointed at their home folder by mistake.
_MAX_DIRECTORIES = 2000

# Never worth watching, and between them they can outnumber a project's own
# files by an order of magnitude.
_SKIP = frozenset({
    ".git", ".hg", ".svn", "__pycache__", "node_modules", ".venv", "venv",
    ".limekit", ".idea", ".vscode", "build", "dist",
})


class FileWatcher(LimeObject, QObject):
    __lime__ = "sys.FileWatcher"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._watcher = QFileSystemWatcher(self)
        self._watcher.directoryChanged.connect(self._onChanged)
        self._watcher.fileChanged.connect(self._onChanged)

        self._pending = set()
        self._onChange = None

        self._settle = QTimer(self)
        self._settle.setSingleShot(True)
        self._settle.setInterval(_SETTLE_MSECS)
        self._settle.timeout.connect(self._flush)

    # -- what to watch -----------------------------------------------------

    @method({"path": "string"}, returns="boolean",
            doc="Watches one file or folder. Returns whether it was added.")
    def watch(self, path):
        if not isinstance(path, str) or not path:
            raise BridgeError(f"expected a path string, got {path!r}")
        if not os.path.exists(path):
            return False
        if path in self._watcher.directories() or path in self._watcher.files():
            return True
        return bool(self._watcher.addPath(path))

    @method({"root": "string"}, returns="integer",
            doc="Watches a folder and every folder beneath it. Returns how "
                "many were added.")
    def watchTree(self, root):
        """Add every directory under `root`.

        Qt's watcher is not recursive, and a project's interesting changes --
        a new file appearing -- happen in whichever folder the author was
        working in, not the one at the top.
        """
        if not os.path.isdir(root):
            return 0

        added = 0
        stack = [root]
        while stack and added < _MAX_DIRECTORIES:
            folder = stack.pop()
            if self.watch(folder):
                added += 1

            # os.scandir rather than fs.FileSystem.listFolder: that one
            # returns a *Lua* table, so calling it from Python needs a bound
            # runtime and raises without one. Reaching back across the bridge
            # to list a folder would be a strange thing for a Python service
            # to do in any case.
            try:
                entries = list(os.scandir(folder))
            except OSError:
                continue                       # unreadable or gone; not fatal

            for entry in entries:
                if entry.name in _SKIP or entry.name.startswith("."):
                    continue
                try:
                    if entry.is_dir(follow_symlinks=False):
                        stack.append(entry.path)
                except OSError:
                    continue

        return added

    @method({"path": "string"}, returns="boolean", doc="Stops watching one path.")
    def unwatch(self, path):
        return bool(self._watcher.removePath(str(path)))

    @method(returns="self", doc="Stops watching everything.")
    def clear(self):
        for group in (self._watcher.directories(), self._watcher.files()):
            if group:
                self._watcher.removePaths(group)
        self._pending.clear()
        self._settle.stop()
        return self

    @method(returns="string[]", doc="Every path currently being watched.")
    def getPaths(self):
        return to_lua(sorted(self._watcher.directories() + self._watcher.files()))

    @method(returns="integer", doc="How many paths are being watched.")
    def getCount(self):
        return len(self._watcher.directories()) + len(self._watcher.files())

    # -- being told --------------------------------------------------------

    @method({"handler": "fun(paths: string[])"}, returns="self",
            doc="Called once, shortly after a change, with the paths that "
                "changed.")
    def setOnChange(self, handler):
        from limekit.kernel.bridge.guard import guard
        self._onChange = guard(handler, widget="FileWatcher", event="onChange")
        return self

    def _onChanged(self, path):
        self._pending.add(path)
        # Restarted on every event, so a burst is reported once when it ends
        # rather than once per event.
        self._settle.start()

    def _flush(self):
        changed = sorted(self._pending)
        self._pending.clear()
        if not changed:
            return

        # A folder that gained a subfolder has to be picked up, or the new
        # one is invisible to every future change inside it.
        for path in changed:
            if os.path.isdir(path):
                self.watchTree(path)

        if self._onChange is not None:
            self._onChange(to_lua(changed))
