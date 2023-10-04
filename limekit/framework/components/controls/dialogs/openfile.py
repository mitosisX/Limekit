from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtWidgets import QFileDialog


class OpenFile(QFileDialog, EnginePart):
    name = "__openFileDialog"

    def __init__(self, parent):
        super().__init__(parent)

    def setInitDir(self, dir):
        self.setDirectory(dir)

    def display(self, parent):
        name, ok = self.getOpenFileName(
            parent,
            "Open File",
            "",
            "Image Files (*.png *.jpg *.bmp);;Text Files (*.txt *.lua)",
            # options=QFileDialog.Option.DontUseNativeDialog,
        )
        return name if name else None

    # Programmatically, use double ;; to support further filters
    # "Images (*.png  *.jpg);;Vector (*.svg)"
    def setAllowedFileTypes(self, types):
        self.setNameFilters()
