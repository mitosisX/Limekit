import lupa
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtGui import QColor


class DropShadow(QGraphicsDropShadowEffect, EnginePart):
    @lupa.unpacks_lua_table
    def __init__(self, widget):
        super().__init__(parent=None)

        self = QGraphicsDropShadowEffect(self)
        self.setBlurRadius(50)
        # shadow.setColor('#7090B0')

        # Calculate alpha value for 15% transparency
        alpha_percentage = 20
        alpha_value = alpha_percentage / 100.0

        # Set shadow color with calculated transparency
        shadow_color = QColor("#7090B0")
        shadow_color.setAlphaF(alpha_value)
        self.setColor(shadow_color)

        self.setOffset(2, 5)
        widget.setGraphicsEffect(self)

    def __init___(self, kwargs):
        super().__init__(parent=None)

        if "offset" in kwargs:
            self.setOffset(int(kwargs["offset"]))

        if "bradius" in kwargs:
            self.setBlurRadius(int(kwargs["bradius"]))

        if "widget" in kwargs:
            widget = kwargs["widget"]
            widget.setGraphicsEffect(self)
