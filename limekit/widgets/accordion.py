"""Collapsible panel stack (QToolBox)."""

from PySide6.QtWidgets import QToolBox, QWidget

from limekit.kernel.bridge.guard import guard
from limekit.kernel.coerce import Icon
from limekit.kernel.spec import Prop
from limekit.widgets.base import LimeWidget, _to_int


class Accordion(LimeWidget, QToolBox):
    __lime__ = "ui.Accordion"

    # currentIndex/setCurrentIndex are the real QToolBox method names -- an
    # intentional shadow, the same shape TextField's plainText/toPlainText
    # avoids and Table's rowCount deliberately does NOT attempt (see table.py).
    # QToolBox has no separate "index means something else" method that would
    # collide, so a Prop is safe here.
    currentIndex = Prop(int, qt=("currentIndex", "setCurrentIndex"))

    def __init__(self):
        super().__init__()
        self._onCurrentChange = None
        self.currentChanged.connect(self._handleCurrentChange)

    def addChild(self, child, label, icon=""):
        self._addItem(child, label, icon)
        return self

    def addLayout(self, layout, label, icon=""):
        widget = QWidget()
        widget.setLayout(layout)
        self._addItem(widget, label, icon)
        return self

    def _addItem(self, child, label, icon):
        if icon:
            self.addItem(child, Icon(icon), str(label))
        else:
            self.addItem(child, str(label))

    def getCount(self):
        return self.count()

    def setOnCurrentChange(self, handler):
        self._onCurrentChange = guard(
            handler, widget="Accordion", event="onCurrentChange"
        )
        return self

    def _handleCurrentChange(self, index):
        if self._onCurrentChange:
            self._onCurrentChange(self, index + 1)
