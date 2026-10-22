"""Running a build as a child process, so progress can be monitored live.

`services/projects.ProjectBuilder` is the guarded wrapper Lua reaches it
through.

Callbacks here are plain callables. `guard()` is applied at the Lua boundary,
not in this module, so it stays usable from plain Python.
"""

import json
import logging

from PySide6.QtCore import QProcess

from limekit.launcher import python_command

logger = logging.getLogger(__name__)

# Keys the build dialog may set, forwarded into the child build script.
_FORWARDED_OPTIONS = ("name", "version", "author", "copyright", "description", "icon")


def _build_script(project_path, options, console_mode, output_dir):
    """The Python source the child process runs to perform the build.

    Every value goes in through repr(), never pasted between quotes: a
    project in a folder called "Bob's App" used to yield a script that did
    not parse. The options travel as JSON inside a repr'd string, since JSON
    is not Python (true/false/null).
    """
    forwarded = {key: options[key] for key in _FORWARDED_OPTIONS if options.get(key)}
    # A yes/no choice, forwarded even when it is "no": the truthiness test
    # above would drop False, and "Pack into a single file" unticked still
    # built a single file.
    if options.get("onefile") is not None:
        forwarded["onefile"] = bool(options["onefile"])

    return f'''
import sys
import json

try:
    from limekit.build.builder import AppBuilder

    options = json.loads({json.dumps(forwarded)!r})

    builder = AppBuilder(
        project_path={str(project_path)!r},
        output_dir={(str(output_dir) if output_dir else None)!r},
        options=options
    )

    success, message, output_path = builder.build(console_mode={bool(console_mode)!r})

    result = {{
        "success": success,
        "message": message,
        "output_path": output_path
    }}
    print("BUILD_RESULT:" + json.dumps(result))

except Exception as e:
    print(f"BUILD_ERROR:{{str(e)}}")
    sys.exit(1)
'''


class BuildProcess:
    """Builds a project in a child process, reporting progress via callbacks."""

    def __init__(self, project_path, options=None):
        self.project_path = project_path
        # Lua hands options across as a table; dict() copes with both that and
        # a real dict, and anything else is treated as "no options".
        try:
            self.options = dict(options) if options is not None else {}
        except (TypeError, ValueError):
            self.options = {}

        self.process = None
        self.onBuildOutput = None
        self.onBuildStarted = None
        self.onBuildFinished = None
        self.onBuildError = None

        self._output_buffer = []
        self._success = False
        self._output_path = None

    # -- callbacks ---------------------------------------------------------

    def setOnBuildOutput(self, callback):
        self.onBuildOutput = callback

    def setOnBuildStarted(self, callback):
        self.onBuildStarted = callback

    def setOnBuildFinished(self, callback):
        self.onBuildFinished = callback

    def setOnBuildError(self, callback):
        self.onBuildError = callback

    # -- lifecycle ---------------------------------------------------------

    def build(self):
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self._handleStdout)
        self.process.readyReadStandardError.connect(self._handleStderr)
        self.process.started.connect(self._handleStarted)
        self.process.finished.connect(self._handleFinished)

        script = _build_script(
            self.project_path,
            self.options,
            self.options.get("console", False),
            self.options.get("output_dir", None),
        )
        self.process.start(python_command(), ["-u", "-c", script])

    def stop(self):
        if self.process and self.process.state() == QProcess.Running:
            self.process.kill()

    # -- results -----------------------------------------------------------

    def getOutput(self):
        return self._output_buffer

    def isSuccess(self):
        return self._success

    def getOutputPath(self):
        return self._output_path

    # -- internals ---------------------------------------------------------

    def _handleStdout(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8").strip()
        if not data:
            return

        self._output_buffer.append(data)
        # The build script prints both markers to stdout; this used to look
        # for BUILD_ERROR only on stderr, so onBuildError never fired.
        self._read_markers(data)

        if self.onBuildOutput:
            self.onBuildOutput(data)

    def _handleStderr(self):
        data = self.process.readAllStandardError().data().decode("utf-8").strip()
        if not data:
            return

        self._output_buffer.append(f"Error: {data}")
        self._read_markers(data)

        if self.onBuildOutput:
            self.onBuildOutput(data)

    def _read_markers(self, data):
        """Act on BUILD_RESULT / BUILD_ERROR lines in a chunk of output.

        A build that finished but failed -- validation, PyInstaller -- is an
        error to the caller too, not only one that raised.
        """
        for line in data.splitlines():
            if line.startswith("BUILD_RESULT:"):
                try:
                    result = json.loads(line[len("BUILD_RESULT:"):])
                except json.JSONDecodeError as exc:
                    logger.warning("Build: Failed to parse build result: %s", exc)
                    continue
                self._success = bool(result.get("success", False))
                self._output_path = result.get("output_path")
                if not self._success:
                    self._report_error(result.get("message") or "the build failed")
            elif line.startswith("BUILD_ERROR:"):
                self._report_error(line[len("BUILD_ERROR:"):])

    def _report_error(self, message):
        if self.onBuildError:
            self.onBuildError(message)

    def _handleStarted(self):
        if self.onBuildStarted:
            self.onBuildStarted()

    def _handleFinished(self, exit_code, exit_status):
        if self.onBuildFinished:
            self.onBuildFinished(self._success, self._output_path)
