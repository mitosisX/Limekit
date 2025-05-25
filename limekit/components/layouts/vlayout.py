from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout
from limekit.engine.parts import EnginePart
from limekit.components.base.layout_base import BaseLayout


class VerticalLayout(BaseLayout, EnginePart):
    name = "VLayout"

    def __init__(self, parent=None):
        super().__init__(QBoxLayout.Direction.TopToBottom, parent=parent)
