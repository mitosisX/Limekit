"""Running a Limekit project as a child process, and working out which engine.

Engine-neutral on purpose. This used to live at
`limekit/core/bootstrap/subprocess_runner.py` -- inside the 1.x tree -- even
though the 2.0 build path needed it too, which is why `limekit/build/` still
imported from `core/`. Both engines and the `sys.ProjectRunner` service now
import it from here instead.

`limekit/core/bootstrap/subprocess_runner.py` re-exports these names so the
1.x engine keeps working unchanged.
"""

import json
import os
import sys
from pathlib import Path

from PySide6.QtCore import QProcess, QTimer

# The two engines need different entry points, and a project run under the
# wrong one fails confusingly: a 2.0 project launched by the 1.x runner dies
# with "module 'limekit.ui' not found", because the 1.x engine injects flat
# globals and never populates package.preload.
LEGACY_ENTRY = ("-c", "from limekit import runner")
MODERN_ENTRY = ("-m", "limekit")


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 2000


def python_command():
    """The interpreter to spawn a project with.

    `sys.executable`, not the bare name "python": the name resolves through
    PATH, which is not necessarily the interpreter this process is running
    under. Inside a virtualenv, or on a machine with several Pythons, the
    one PATH finds may have no limekit installed, and Run failed with
    "No module named limekit" while the launcher itself was working fine.

    When the launcher has been frozen, `sys.executable` is the launcher's
    own executable rather than an interpreter, so there is nothing here that
    can run a project as a child process -- see `can_spawn_projects`.
    """
    return sys.executable or ("python" if os.name == "nt" else "python3")


def can_spawn_projects():
    """Whether this process can start a project in a child process.

    False in a frozen launcher: there is no Python interpreter to invoke,
    only the bundled application. A launcher that has been built into an
    executable needs another way to run the projects it opens, and should
    say so rather than spawning something that cannot work.
    """
    return not getattr(sys, "frozen", False)


def detect_api_version(project_path):
    """Return "2.0" or "1.0" for the project at `project_path`.

    Explicit wins: `app.json` may declare `{"api": "2.0"}`. That is the
    documented way to mark a project, and it is checked first.

    Otherwise fall back to a structural signal -- a 2.0 project must
    `require("limekit.<module>")`, because 2.0 injects no globals at all,
    while 1.x had no module system to require from. This keeps the existing
    projects working untouched (none of them require anything) without
    forcing a migration flag on people just to press Run.

    Anything unreadable or ambiguous is treated as 1.0: that is the
    behaviour every existing project already relies on.
    """
    root = Path(project_path)

    try:
        declared = json.loads((root / "app.json").read_text(encoding="utf-8"))
        api = declared.get("api") or declared.get("project", {}).get("api")
        if api is not None:
            return "2.0" if str(api).startswith("2") else "1.0"
    except (OSError, ValueError, AttributeError):
        pass                        # no app.json, or malformed -- fall through

    try:
        source = (root / "scripts" / "main.lua").read_text(
            encoding="utf-8", errors="ignore"
        )
        if 'require("limekit.' in source or "require('limekit." in source:
            return "2.0"
    except OSError:
        pass

    return "1.0"


def entry_for(project_path):
    """The interpreter arguments that launch this project's engine."""
    return MODERN_ENTRY if detect_api_version(project_path) == "2.0" else LEGACY_ENTRY


# Implemented on 24 November, 2023 12:21 PM (Friday)
class ProjectRunner(QProcess):
    """Runs a project in a child process, reporting output back through callbacks.

    The callbacks here are plain callables. Anything crossing the Lua bridge
    is wrapped by `limekit.services.projects`, which is where `guard()` is
    applied -- this class stays usable from Python without a Lua runtime.
    """

    onProcessReadyRead = None
    onProcessStarted = None
    onProcessFinished = None

    def __init__(self, project_path):
        super().__init__(parent=None)

        self.project_path = project_path  # The path to the user's project
        self._stopping = False

        # Errors go to stderr, and a console reading only stdout showed a
        # project exiting with code 1 and no reason -- the traceback naming
        # the file and line was thrown away. Merge the channels so the
        # output a user sees is the output the project produced.
        self.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)

        self.readyRead.connect(self._handleReadOutput)
        self.started.connect(self._handleProcessStarted)
        self.finished.connect(self._handleProcessFinished)

    def command(self):
        """The argument list this runner will spawn. Worth showing a user:
        which engine a project runs on is decided per project, so seeing the
        command answers "why did it run like that?" without guesswork."""
        return [python_command(), "-u", *entry_for(self.project_path),
                self.project_path]

    def run(self):
        self._stopping = False
        # -u so the child does not buffer its output; a console that only
        # fills in at exit is no use while the app is running.
        self.start(self.command()[0], self.command()[1:])

    def stop(self, grace_msecs=2000):
        """Ask the project to close, and insist only if it will not.

        `kill()` alone gave the project no chance to run its onClose
        handler, and reported the shutdown as a crash afterwards -- pressing
        Stop looked identical to the app falling over.
        """
        self._stopping = True
        self.terminate()

        def insist():
            if self.state() != QProcess.ProcessState.NotRunning:
                self.kill()

        QTimer.singleShot(_to_int(grace_msecs), insist)

    def wasStopped(self):
        """Whether the last exit followed a `stop()` rather than the project
        finishing on its own."""
        return self._stopping

    def setOnProcessReadyRead(self, onProcessReadyRead):
        self.onProcessReadyRead = onProcessReadyRead

    def setOnProcessStarted(self, onProcessStarted):
        self.onProcessStarted = onProcessStarted

    def setOnProcessFinished(self, onProcessFinished):
        self.onProcessFinished = onProcessFinished

    def _handleReadOutput(self):
        progressText = str(self.readAll().data().decode("utf-8")).rstrip()

        if self.onProcessReadyRead:
            self.onProcessReadyRead(progressText)

    def _handleProcessFinished(self, exit_code=0, exit_status=None):
        if not self.onProcessFinished:
            return
        crashed = (exit_status == QProcess.ExitStatus.CrashExit
                   and not self._stopping)
        self.onProcessFinished(int(exit_code), bool(crashed))

    def _handleProcessStarted(self):
        if self.onProcessStarted:
            self.onProcessStarted()
