from limekit.framework.core.engine.parts import EnginePart


class PythonParamsException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
