from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.components.base.base_layout import BaseLayout


class VerticalLayout(BaseLayout, EnginePart):
    name = "VLayout"

    def __init__(self):
        super().__init__(QBoxLayout.Direction.TopToBottom, parent=None)
