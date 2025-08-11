from PySide6.QtCore import Property
from limekit.engine.parts import EnginePart


class QProperty(EnginePart):
    name = "Property"

    def __init__(self, _type, getter=None, setter=None, notifier=None):
        print("$$$$$$$$$$$$$ ", _type)
        print("$$$$$$$$$$$$$ ", getter)
        print("$$$$$$$$$$$$$ ", setter)
        print("$$$$$$$$$$$$$ ", notifier)

        self.property = Property(type=_type, fget=getter, fset=setter, notify=notifier)
