import sys
from limekit.framework.core.engine.parts import EnginePart


class State:
    name = "__engineState"

    @staticmethod
    def isIDE(self):
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            # print("running in a PyInstaller bundle")
            return False
        else:
            return True
            # print("running in a normal Python process")
