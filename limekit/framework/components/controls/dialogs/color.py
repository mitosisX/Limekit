from PySide6.QtWidgets import QColorDialog
from limekit.framework.core.engine.parts import EnginePart


class ColorPicker(EnginePart):
    name = "__colorPicker"

    def __init__(self):
        self.color = QColorDialog.getColor()

    def getHex(self):
        return self.color.name()

    def getRGB(self):
        return self.color.getRgb()
