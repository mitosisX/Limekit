"""A layout that shows one child at a time.

`currentIndex` can't be a `Prop`: Qt's is 0-indexed and the accessor needs
translation, the same reason `LimeLayout.getChildAt` (base.py) and
`Tab.setCurrentIndex` are hand-written. `setMargins`/`getChildAt`/`getCount`
already come from `LimeLayout` -- 1.x hand-rolled its own copies of all
three (badly: `addLayout` called `self.addChildLayout`, a method
`QStackedLayout` does not have, so it was dead and unreachable). `addLayout`
here wraps the layout in a plain `QWidget` instead, the same trick
`SlidingStackedWidget.addLayout` and `Accordion.addLayout` use.
"""

from PySide6.QtWidgets import QStackedLayout, QWidget

from limekit.kernel.coerce import LuaIndex
from limekit.layouts.base import LimeLayout


class StackedLayout(LimeLayout, QStackedLayout):
    __lime__ = "ui.StackedLayout"

    def __init__(self):
        super().__init__()

    def addChild(self, child):
        self.addWidget(child)
        return self

    def addLayout(self, layout):
        widget = QWidget()
        widget.setLayout(layout)
        self.addWidget(widget)
        return self

    def setCurrentIndex(self, index):
        super().setCurrentIndex(LuaIndex(index))
        return self

    def getCurrentIndex(self):
        return self.currentIndex() + 1
