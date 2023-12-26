import os
from PySide6.QtCore import QProcess


# class Starter:
#     name = "__appCore"

#     @classmethod
#     def run_project(cls, callback):
#         process = QProcess(cls)
#         process.readyRead.connect(cls.readOutput)
#         process.started.connect(cls.processStarted)
#         process.finished.connect(cls.processFinished)
#         process.start("python", ["-u", "main.py"])

#     @staticmethod
#     def run_project_(path, callback):
#         # process = subprocess.run(
#         #     f"python main.py {path}",
#         #     capture_output=True
#         #     # encoding="utf-8",
#         # )

#         # return process.stdout

#         # callback(
#         #     subprocess.check_output(
#         #         [
#         #             "python",
#         #             "main.py",
#         #             os.path.join(path, ""),
#         #         ]
#         #     ).decode("utf-8")
#         # )
#         return subprocess.check_output(
#             [
#                 "python",
#                 "-c",
#                 "from limekit.framework.run import *",
#                 os.path.join(path, ""),
#             ]
#         ).decode("utf-8")


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

    # Windows uses python, while macOS uses python3 to execute python
    # Take this into consideration
    def run(self):
        # Initially, the approach failed for lack of -u flag; this flashes stdout stream out
        # immediately

        self.start(
            # nt refers to Windows
            "python" if os.name == "nt" else "python3",
            [
                "-u",
                "-c",
                "from limekit.framework.run import *",
                self.project_path,
            ],
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

        # endText = "Finished"

    def _handleProcessStarted(self):
        if self.onProcessStarted:
            self.onProcessStarted()

        # startText = "Started"
