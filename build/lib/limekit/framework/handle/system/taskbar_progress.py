import PyTaskbar

"""
Doesn't seem to be working

States: loading, normal, warning, error, done
"""


class TaskbarProgress:
    def __init__(self):
        self.taskprogress = PyTaskbar.Progress()
        self.taskprogress.init()
        self.setState("normal")
        self.setProgress(10)

    def setState(self, state):
        self.taskprogress.setState(state)

    def setProgress(self, progress):
        self.taskprogress.setProgress(progress)

    def getStates(self):
        return ["loading", "normal", "warning", "error", "done"]
