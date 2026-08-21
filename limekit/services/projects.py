"""Running and building Limekit projects: `require("limekit.sys")`.

The 2.0 replacements for 1.x's `app.runProject(path)` and
`app.buildProject(path, options)`. Those were the last two globals with no
2.0 equivalent, and the reason Limer itself could not be ported.

Both wrap an engine-neutral implementation (`limekit.launcher.ProjectRunner`,
`limekit.build.runner.BuildProcess`) rather than reimplementing it, so the
1.x and 2.0 paths cannot drift apart. What this module adds is the Lua
boundary: every callback crosses `guard()`, so an error inside a Lua handler
is reported rather than escaping into the Qt event loop.
"""

from PySide6.QtCore import QObject

from limekit.build.runner import BuildProcess
from limekit.kernel.bridge.convert import as_mapping, to_lua
from limekit.kernel.bridge.guard import guard
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import method
from limekit.launcher import ProjectRunner as _ProjectRunner
from limekit.launcher import can_spawn_projects, detect_api_version


def _require_path(value, label):
    if not isinstance(value, str) or not value:
        raise BridgeError(f"expected a project path for {label}, got {value!r}")
    return value


class ProjectRunner(LimeObject, QObject):
    """Runs a Limekit project in a child process.

    Replaces 1.x's `app.runProject(path)`. Which engine the project runs on
    is decided per project -- see `getApiVersion` -- so a 2.0 launcher can
    run 1.x projects and vice versa.
    """

    __lime__ = "sys.ProjectRunner"

    def __init__(self, project_path):
        super().__init__()
        self._path = _require_path(project_path, "ProjectRunner")
        self._process = _ProjectRunner(self._path)

    @method({"handler": "fun(output: string)"}, returns="self",
            doc="Runs when the project writes to stdout or stderr.")
    def setOnProcessReadyRead(self, handler):
        self._process.setOnProcessReadyRead(
            guard(handler, widget="ProjectRunner", event="onProcessReadyRead")
        )
        return self

    @method({"handler": "fun()"}, returns="self",
            doc="Runs once the child process has started.")
    def setOnProcessStarted(self, handler):
        self._process.setOnProcessStarted(
            guard(handler, widget="ProjectRunner", event="onProcessStarted")
        )
        return self

    @method({"handler": "fun(exit_code: integer, crashed: boolean)"}, returns="self",
            doc="Runs when the project exits, however it exits. The handler "
                "receives the exit code and whether it crashed -- pressing "
                "Stop is not a crash.")
    def setOnProcessFinished(self, handler):
        self._process.setOnProcessFinished(
            guard(handler, widget="ProjectRunner", event="onProcessFinished")
        )
        return self

    @method(returns="self", doc="Starts the project.")
    def run(self):
        self._process.run()
        return self

    @method(returns="self", doc="Stops the project.")
    def stop(self):
        self._process.stop()
        return self

    @method(returns="boolean", doc="Whether the project is currently running.")
    def isRunning(self):
        from PySide6.QtCore import QProcess
        return self._process.state() != QProcess.ProcessState.NotRunning

    @method(returns="string",
            doc='The engine this project will run on: "1.0" or "2.0".')
    def getApiVersion(self):
        return detect_api_version(self._path)

    @method(returns="string", doc="The project folder this runner was created for.")
    def getPath(self):
        return self._path

    @staticmethod
    @method(returns="boolean",
            doc="Whether this build can run a project at all. False in a "
                "launcher that has been built into an executable: there is "
                "no interpreter left to start a child process with.")
    def canSpawnProjects():
        return can_spawn_projects()

    @method(returns="string[]",
            doc="The command this runner spawns, as a table of arguments.")
    def getCommand(self):
        return to_lua(self._process.command())

    @method(returns="integer",
            doc="The operating system's id for the running process, or 0 if "
                "it is not running.")
    def getProcessId(self):
        return int(self._process.processId())

    @method(returns="boolean",
            doc="Whether the last exit followed a stop() rather than the "
                "project finishing on its own.")
    def wasStopped(self):
        return self._process.wasStopped()


class ProjectBuilder(LimeObject, QObject):
    """Builds a Limekit project into a standalone executable.

    Replaces 1.x's `app.buildProject(path, options)`. Options are a table:
    `console` (show a terminal window), `output_dir`, and the metadata the
    build dialog collects -- `name`, `version`, `author`, `copyright`,
    `description`, `icon`.
    """

    __lime__ = "sys.ProjectBuilder"

    def __init__(self, project_path, options=None):
        super().__init__()
        self._path = _require_path(project_path, "ProjectBuilder")
        self._process = BuildProcess(self._path, as_mapping(options))

    @method({"handler": "fun(line: string)"}, returns="self",
            doc="Runs for each line the build writes. Use it to drive a console view.")
    def setOnBuildOutput(self, handler):
        self._process.setOnBuildOutput(
            guard(handler, widget="ProjectBuilder", event="onBuildOutput")
        )
        return self

    @method({"handler": "fun()"}, returns="self",
            doc="Runs once the build has started.")
    def setOnBuildStarted(self, handler):
        self._process.setOnBuildStarted(
            guard(handler, widget="ProjectBuilder", event="onBuildStarted")
        )
        return self

    @method({"handler": "fun(success: boolean, output_path: string)"}, returns="self",
            doc="Runs when the build finishes, successfully or not.")
    def setOnBuildFinished(self, handler):
        self._process.setOnBuildFinished(
            guard(handler, widget="ProjectBuilder", event="onBuildFinished")
        )
        return self

    @method({"handler": "fun(message: string)"}, returns="self",
            doc="Runs if the build fails with an error.")
    def setOnBuildError(self, handler):
        self._process.setOnBuildError(
            guard(handler, widget="ProjectBuilder", event="onBuildError")
        )
        return self

    @method(returns="self", doc="Starts the build.")
    def build(self):
        self._process.build()
        return self

    @method(returns="self", doc="Stops a build in progress.")
    def stop(self):
        self._process.stop()
        return self

    @method(returns="boolean", doc="Whether the finished build succeeded.")
    def isSuccess(self):
        return self._process.isSuccess()

    @method(returns="string",
            doc="Path to the built executable, once the build has finished.")
    def getOutputPath(self):
        return self._process.getOutputPath()

    @method(returns="string[]", doc="Every line the build has produced so far.")
    def getOutput(self):
        return to_lua(list(self._process.getOutput()))

    @method(returns="string", doc="The project folder this builder was created for.")
    def getPath(self):
        return self._path
