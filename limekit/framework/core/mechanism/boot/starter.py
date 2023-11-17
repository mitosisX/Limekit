import os
import subprocess
from PySide6.QtCore import QProcess, Signal
from limekit.framework.core.engine.parts import EnginePart


class Starter(EnginePart):
    name = "__appCore"

    @staticmethod
    def run_project(path, callback):
        # process = subprocess.run(
        #     f"python main.py {path}",
        #     capture_output=True
        #     # encoding="utf-8",
        # )

        # return process.stdout

        # callback(
        #     subprocess.check_output(
        #         [
        #             "python",
        #             "main.py",
        #             os.path.join(path, ""),
        #         ]
        #     ).decode("utf-8")
        # )
        return subprocess.check_output(
            [
                "python",
                "-c",
                "from limekit.framework.run import *",
                os.path.join(path, ""),
            ]
        ).decode("utf-8")


class ProcessOutputReader(QProcess):
    def __init__(self):
        super().__init__(parent=None)

        # merge stderr channel into stdout channel
        self.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)

        raw_bytes = self.readAllStandardOutput()
        text = raw_bytes.data().decode("utf-8")  # Assuming utf-8 encoding

        print(text)
