from PySide6.QtWidgets import QFrame
from PySide6.QtCore import Qt
from limekit.engine.parts import EnginePart


class Separator(QFrame, EnginePart):
    def __init__(self, orientation="horizontal", parent=None):
        super().__init__(parent)
        self.set_orientation(orientation)

        # Default styling
        self.setLineWidth(1)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setMidLineWidth(0)

    # Private method to set the frame shape based on orientation
    def set_orientation(self, orientation):
        """Set the orientation of the separator.

        Args:
            orientation (str): "horizontal" or "vertical"
        """
        orientation = orientation.lower()
        if orientation == "horizontal":
            self.setFrameShape(QFrame.Shape.HLine)
        elif orientation == "vertical":
            self.setFrameShape(QFrame.Shape.VLine)
        else:
            raise ValueError(
                f"Invalid orientation: {orientation}. Must be 'horizontal' or 'vertical'"
            )
