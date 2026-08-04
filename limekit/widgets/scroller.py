"""A scrollable viewport around a child widget or layout.

`onScroll` connects to `verticalScrollBar().valueChanged`, a signal that
lives on a child object rather than on the Scroller itself, so it cannot use
the declarative `Event` spec (which resolves `getattr(self, signal_name)` on
the instance). Hand-written, but still guarded like every other handler.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QWidget

from limekit.kernel.bridge.guard import guard
from limekit.kernel.coerce import Enum
from limekit.kernel.spec import Prop
from limekit.widgets.base import LimeWidget

_SCROLLBAR_POLICIES = {
    "overflow": Qt.ScrollBarPolicy.ScrollBarAsNeeded,
    "hidden": Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
    "alwayson": Qt.ScrollBarPolicy.ScrollBarAlwaysOn,
}
_scrollbar_policy = Enum(_SCROLLBAR_POLICIES, "scrollbar behavior")


class Scroller(LimeWidget, QScrollArea):
    __lime__ = "ui.Scroller"

    resizable = Prop(bool, qt=("widgetResizable", "setWidgetResizable"))

    def __init__(self):
        super().__init__()
        self._central = QWidget()
        self.setWidget(self._central)
        self.setResizable(True)
        self.setHorizontalScrollBarBehavior("overflow")
        self.setVerticalScrollBarBehavior("overflow")
        self._onScroll = None
        self.verticalScrollBar().valueChanged.connect(self._handleScroll)

    def _handleScroll(self, value):
        if self._onScroll:
            self._onScroll(self, value)

    def setOnScroll(self, handler):
        self._onScroll = guard(handler, widget="Scroller", event="onScroll")
        return self

    def setChild(self, child):
        self._central = child
        self.setWidget(child)
        return self

    def getChild(self):
        return self.widget()

    def setLayout(self, layout):
        self._central.setLayout(layout)
        return self

    def getLayout(self):
        return self._central.layout()

    def maxVerticalScroll(self):
        return self.verticalScrollBar().maximum()

    def minVerticalScroll(self):
        return self.verticalScrollBar().minimum()

    def maxHorizontalScroll(self):
        return self.horizontalScrollBar().maximum()

    def minHorizontalScroll(self):
        return self.horizontalScrollBar().minimum()

    def setHorizontalScrollBarBehavior(self, behavior):
        super().setHorizontalScrollBarPolicy(_scrollbar_policy(behavior))
        return self

    def setVerticalScrollBarBehavior(self, behavior):
        super().setVerticalScrollBarPolicy(_scrollbar_policy(behavior))
        return self
