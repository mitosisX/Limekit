from PySide6.QtWidgets import QBoxLayout, QLayout
from limekit.engine.parts import EnginePart
from PySide6.QtCore import Qt
from limekit.components.base.base_layout import BaseLayout


class HorizontalLayout(BaseLayout, EnginePart):
    name = "HLayout"

    def __init__(self, parent=None):
        super().__init__(QBoxLayout.Direction.LeftToRight, parent=parent)
