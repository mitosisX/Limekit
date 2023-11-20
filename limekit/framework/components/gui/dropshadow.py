import lupa
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from limekit.framework.core.engine.parts import EnginePart


class DropShadow(QGraphicsDropShadowEffect, EnginePart):
    @lupa.unpacks_lua_table
    def __init__(self, kwargs):
        super().__init__(parent=None)

        if "offset" in kwargs:
            self.setOffset(int(kwargs["offset"]))

        if "bradius" in kwargs:
            self.setBlurRadius(int(kwargs["bradius"]))

        if "widget" in kwargs:
            widget = kwargs["widget"]
            widget.setGraphicsEffect(self)
