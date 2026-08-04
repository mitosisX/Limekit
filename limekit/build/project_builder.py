"""
Limekit Project Builder
QProcess-based builder that can be monitored from Lua/Limer
Similar to subprocess_runner.py but for building apps
"""

import os
import sys
import json
from PySide6.QtCore import QProcess

from limekit.engine.parts import EnginePart


class ProjectBuilder(EnginePart):
    """
    QProcess-based project builder that allows Limer to monitor build progress.
    Exposes the same callback pattern as ProjectRunner for consistency.
    """

    name = "__appBuild"

    onBuildOutput = None
    onBuildStarted = None
    onBuildFinished = None
    onBuildError = None

    def __init__(self, project_path: str, options=None):
        self.project_path = project_path
        # Convert Lua table to Python dict if needed
        if options is not None:
            try:
                self.options = dict(options)
            except (TypeError, ValueError):
                self.options = {}
        else:
            self.options = {}
        self.process = None
        self._output_buffer = []
        self._success = False
        self._output_path = None

    def setOnBuildOutput(self, callback):
        """Set callback for build output (similar to setOnProcessReadyRead)."""
        self.onBuildOutput = callback

    def setOnBuildStarted(self, callback):
        """Set callback for build start."""
        self.onBuildStarted = callback

    def setOnBuildFinished(self, callback):
        """Set callback for build completion."""
        self.onBuildFinished = callback

    def setOnBuildError(self, callback):
        """Set callback for build errors."""
        self.onBuildError = callback

    def build(self):
        """Start the build process."""
        self.process = QProcess()

        self.process.readyReadStandardOutput.connect(self._handleStdout)
        self.process.readyReadStandardError.connect(self._handleStderr)
        self.process.started.connect(self._handleStarted)
        self.process.finished.connect(self._handleFinished)

        # Get build options
        console_mode = self.options.get("console", False)
        output_dir = self.options.get("output_dir", None)

        # Build the command
        build_script = self._create_build_script(console_mode, output_dir)

        # Start the build process
        python_cmd = "python" if os.name == "nt" else "python3"
        self.process.start(python_cmd, ["-u", "-c", build_script])

    def _create_build_script(self, console_mode: bool, output_dir: str) -> str:
        """Create the Python script that performs the actual build."""
        # Escape backslashes for Windows paths
        project_path_escaped = self.project_path.replace('\\', '\\\\')
        output_dir_escaped = output_dir.replace('\\', '\\\\') if output_dir else None
        output_dir_str = f"'{output_dir_escaped}'" if output_dir_escaped else "None"

        # Build options dictionary for passing to builder
        options_dict = {}
        for key in ['name', 'version', 'author', 'copyright', 'description', 'icon']:
            value = self.options.get(key)
            if value:
                # Escape backslashes in paths
                if key == 'icon':
                    value = value.replace('\\', '\\\\')
                options_dict[key] = value

        # Convert options to string representation
        options_str = json.dumps(options_dict)

        script = f'''
import sys
import json

try:
    from limekit.build.builder import AppBuilder

    # Build options from dialog
    options = {options_str}

    builder = AppBuilder(
        project_path='{project_path_escaped}',
        output_dir={output_dir_str},
        options=options
    )

    success, message, output_path = builder.build(console_mode={console_mode})

    # Output result as JSON for parsing
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
        return script

    def stop(self):
        """Stop the build process."""
        if self.process and self.process.state() == QProcess.Running:
            self.process.kill()

    def _handleStdout(self):
        """Handle standard output from build process."""
        data = self.process.readAllStandardOutput().data().decode("utf-8").strip()

        if data:
            self._output_buffer.append(data)

            # Check for build result
            if "BUILD_RESULT:" in data:
                try:
                    result_json = data.split("BUILD_RESULT:")[1]
                    result = json.loads(result_json)
                    self._success = result.get("success", False)
                    self._output_path = result.get("output_path")
                except (json.JSONDecodeError, IndexError) as e:
                    from limekit.core.error_handler import warn
                    warn(f"Failed to parse build result: {e}", "Build")

            if self.onBuildOutput:
                self.onBuildOutput(data)

    def _handleStderr(self):
        """Handle standard error from build process."""
        data = self.process.readAllStandardError().data().decode("utf-8").strip()

        if data:
            self._output_buffer.append(f"Error: {data}")

            if "BUILD_ERROR:" in data:
                error_msg = data.split("BUILD_ERROR:")[1] if "BUILD_ERROR:" in data else data
                if self.onBuildError:
                    self.onBuildError(error_msg)

            if self.onBuildOutput:
                self.onBuildOutput(data)

    def _handleStarted(self):
        """Handle build process started."""
        if self.onBuildStarted:
            self.onBuildStarted()

    def _handleFinished(self, exit_code, exit_status):
        """Handle build process finished."""
        if self.onBuildFinished:
            self.onBuildFinished(self._success, self._output_path)

    def getOutput(self) -> list:
        """Get all build output."""
        return self._output_buffer

    def isSuccess(self) -> bool:
        """Check if build was successful."""
        return self._success

    def getOutputPath(self) -> str:
        """Get the path to the built executable."""
        return self._output_path
