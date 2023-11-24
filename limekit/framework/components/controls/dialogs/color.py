from PySide6.QtWidgets import QColorDialog
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.handle.scripts.swissknife.converters import Converter


class ColorPicker(QColorDialog, EnginePart):
    name = "__colorPicker"

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.dialog = self.exec()
        # self.color = self.getColor()

    def display(self, type_="rgb"):
        if self.dialog:
            if type_ == "hex":
                return self.currentColor().name()

            elif type_ == "rgb":
                r, g, b = (
                    self.currentColor().red(),
                    self.currentColor().green(),
                    self.currentColor().blue(),
                )

                return Converter.table_from({"r": r, "g": g, "b": b})
