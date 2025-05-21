from PySide6.QtWidgets import QSpacerItem
from limekit.engine.parts import EnginePart


# Used in layouts (lay:addSpacer(spacer))
class Spacer(QSpacerItem, EnginePart):
    def __init__(self, width, height):
        super().__init__(width, height)
