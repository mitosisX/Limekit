from PySide6.QtCore import QRegularExpression
from limekit.framework.core.engine.parts import EnginePart


# Used in app table
class RegularExpression(QRegularExpression, EnginePart):
    onHighlightBlockFunc = None

    def __init__(self, regex):
        super().__init__(regex)
