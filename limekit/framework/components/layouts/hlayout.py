from PySide6.QtWidgets import QBoxLayout, QLayout
from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtCore import Qt
from limekit.framework.components.base.base_layout import BaseLayout


class HorizontalLayout(BaseLayout, EnginePart):
    name = "HLayout"

    def __init__(self):
        super().__init__(QBoxLayout.Direction.LeftToRight, parent=None)
