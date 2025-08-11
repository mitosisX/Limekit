from PySide6.QtCore import QObject, Signal, Property
from limekit.engine.parts import EnginePart


class Controller(QObject, EnginePart):
    textChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._text = "Text"

    def getText(self):
        return self._text

    def setText(self, value):
        if self._text != value:
            self._text = value
            self.textChanged.emit()

    text = Property(str, getText, setText, notify=textChanged)


# class Controller(QObject, EnginePart):
#     def __init__(self):
#         super().__init__()

#     @classmethod
#     def setValue(cls, name, value):
#         """Set a class-level variable dynamically."""
#         print("//// ", value)
#         setattr(cls, name, value)

#     @classmethod
#     def getValue(cls, name, default=None):
#         """Get a class-level variable (returns default if not found)."""
#         return getattr(cls, name, default)
