from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtWidgets import QFileDialog


class FolderPicker(QFileDialog, EnginePart):
    name = "__folderPickerDialog"

    def __init__(self):
        super().__init__()

    def display(self, parent, title, dir):
        folder = self.getExistingDirectory(
            parent, title, dir, options=QFileDialog.Option.ShowDirsOnly
        )

        return folder if folder else ""
