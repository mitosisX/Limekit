import json
import os
from pathlib import Path

from PySide6.QtCore import QProcess

# The two engines need different entry points, and a project run under the
# wrong one fails confusingly: a 2.0 project launched by the 1.x runner dies
# with "module 'limekit.ui' not found", because the 1.x engine injects flat
# globals and never populates package.preload.
LEGACY_ENTRY = ("-c", "from limekit import runner")
MODERN_ENTRY = ("-m", "limekit")


def detect_api_version(project_path):
    """Return "2.0" or "1.0" for the project at `project_path`.

    Explicit wins: `app.json` may declare `{"api": "2.0"}`. That is the
    documented way to mark a project, and it is checked first.

    Otherwise fall back to a structural signal -- a 2.0 project must
    `require("limekit.<module>")`, because 2.0 injects no globals at all,
    while 1.x had no module system to require from. This keeps the ~52
    existing projects working untouched (none of them require anything)
    without forcing a migration flag on people just to press Run.

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


# Implemented on 24 November, 2023 12:21 PM (Friday)
class ProjectRunner(QProcess):
    onProcessReadyRead = None
    onProcessStarted = None
    onProcessFinished = None

    def __init__(self, project_path):
        super().__init__(parent=None)

        self.project_path = project_path  # The path to the user's project

        self.readyRead.connect(self._handleReadOutput)
        self.started.connect(self._handleProcessStarted)
        self.finished.connect(self._handleProcessFinished)

    # Windows uses "python", Linux & macOS use "python3" to execute python
    # Take this into consideration
    def run(self):
        # -u for capture stdout
        entry = (
            MODERN_ENTRY
            if detect_api_version(self.project_path) == "2.0"
            else LEGACY_ENTRY
        )

        self.start(
            # nt refers to Windows
            "python" if os.name == "nt" else "python3",
            ["-u", *entry, self.project_path],
        )

    def stop(self):
        self.kill()

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

    def _handleProcessFinished(self):
        if self.onProcessFinished:
            self.onProcessFinished()

    def _handleProcessStarted(self):
        if self.onProcessStarted:
            self.onProcessStarted()
