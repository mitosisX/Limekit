"""Running a build as a child process, so progress can be monitored live.

Engine-neutral. `build/project_builder.py` was the same logic welded to
`EnginePart`, the 1.x base class, which meant the 2.0 side could not reuse it
without dragging in the legacy engine. The behaviour lives here now;
`project_builder.ProjectBuilder` is a thin 1.x shim over it, and
`services/projects.ProjectBuilder` is the guarded 2.0 wrapper.

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
    """The Python source the child process runs to perform the build."""
    project_path_escaped = project_path.replace("\\", "\\\\")
    output_dir_escaped = output_dir.replace("\\", "\\\\") if output_dir else None
    output_dir_str = f"'{output_dir_escaped}'" if output_dir_escaped else "None"

    forwarded = {}
    for key in _FORWARDED_OPTIONS:
        value = options.get(key)
        if value:
            if key == "icon":
                value = value.replace("\\", "\\\\")
            forwarded[key] = value

    options_str = json.dumps(forwarded)

    return f'''
import sys
import json

try:
    from limekit.build.builder import AppBuilder

    options = {options_str}

    builder = AppBuilder(
        project_path='{project_path_escaped}',
        output_dir={output_dir_str},
        options=options
    )

    success, message, output_path = builder.build(console_mode={console_mode})

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

        if "BUILD_RESULT:" in data:
            try:
                result = json.loads(data.split("BUILD_RESULT:")[1])
                self._success = result.get("success", False)
                self._output_path = result.get("output_path")
            except (json.JSONDecodeError, IndexError) as exc:
                logger.warning("Build: Failed to parse build result: %s", exc)

        if self.onBuildOutput:
            self.onBuildOutput(data)

    def _handleStderr(self):
        data = self.process.readAllStandardError().data().decode("utf-8").strip()
        if not data:
            return

        self._output_buffer.append(f"Error: {data}")

        if "BUILD_ERROR:" in data and self.onBuildError:
            self.onBuildError(data.split("BUILD_ERROR:")[1])

        if self.onBuildOutput:
            self.onBuildOutput(data)

    def _handleStarted(self):
        if self.onBuildStarted:
            self.onBuildStarted()

    def _handleFinished(self, exit_code, exit_status):
        if self.onBuildFinished:
            self.onBuildFinished(self._success, self._output_path)
