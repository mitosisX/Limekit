from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QDialogButtonBox
from limekit.framework.core.engine.parts import EnginePart

"""
This is a Dumb Dialog. Oftenly used for "Ok", "Cancel" operations
"""


class DialogBox(QDialog, EnginePart):
    name = "Modal"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.button(QDialogButtonBox.Ok).setDefault(True)

    def addLayout(self, lay):
        super().setLayout(lay)
