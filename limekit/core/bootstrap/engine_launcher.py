from limekit.engine.parts import EnginePart
from limekit.core.bootstrap.subprocess_runner import ProjectRunner


class ProcessRunner(EnginePart):
    name = "__appCore"

    def __init__(self, project_path):
        self.runner = ProjectRunner(project_path)

    def setOnProcessReadyRead(self, onProcessReadyRead):
        self.runner.setOnProcessReadyRead(onProcessReadyRead)

    def setOnProcessStarted(self, onProcessStarted):
        self.runner.setOnProcessStarted(onProcessStarted)

    def setOnProcessFinished(self, onProcessFinished):
        self.runner.setOnProcessFinished(onProcessFinished)

    def run(self):
        self.runner.run()

    def stop(self):
        self.runner.stop()
