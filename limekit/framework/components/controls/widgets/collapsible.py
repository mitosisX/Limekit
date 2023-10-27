from PySide6.QtWidgets import QToolBox, QWidget
from PySide6.QtGui import QIcon
from limekit.framework.core.engine.parts import EnginePart


class Collapsible(QToolBox, EnginePart):
    onValueChangedFunc = None

    def __init__(self):
        super().__init__()

    def addChild(self, child, label, icon=""):
        self._addItem(child, label, icon)

    def addLayout(self, layout, label, icon=""):
        widget = QWidget()
        widget.setLayout(layout)
        self._addItem(widget, label, icon)

    def _addItem(self, child, label, icon=""):
        if icon:
            super().addItem(child, QIcon(icon), label)
            return

        super().addItem(child, label)
