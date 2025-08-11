from PySide6.QtCore import QObject, Signal, Property
from limekit.engine.parts import EnginePart


class Bridge(QObject, EnginePart):
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
#         self._dynamic_values = {}

#     def setValue(self, key, value):
#         """Dynamically set an attribute."""
#         self._dynamic_values[key] = value

#     def getValue(self, key, default=None):
#         """Get a dynamically set attribute."""
#         return self._dynamic_values.get(key, default)

#     def __getattr__(self, name):
#         """Allow access via Class.name (falls back to _dynamic_values)."""
#         if name in self._dynamic_values:
#             return self._dynamic_values[name]

#         raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

#     def __setattr__(self, name, value):
#         """Allow setting via Class.name = value."""
#         super().__setattr__(name, value)
