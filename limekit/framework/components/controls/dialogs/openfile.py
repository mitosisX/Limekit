from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtWidgets import QFileDialog


class OpenFile(QFileDialog, EnginePart):
    name = "__openFileDialog"

    def __init__(self, parent):
        super().__init__(parent)
