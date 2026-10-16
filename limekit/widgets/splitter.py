from PySide6.QtWidgets import QSplitter, QWidget

from limekit.kernel.bridge.convert import as_sequence
from limekit.kernel.coerce import ORIENTATIONS, Enum
from limekit.kernel.spec import Event, Prop, method
from limekit.widgets.base import LimeWidget, _to_int

_orientation = Enum(ORIENTATIONS, "orientation")


def _to_size_list(value):
    return [_to_int(v, "size") for v in as_sequence(value)]


class Splitter(LimeWidget, QSplitter):
    __lime__ = "ui.Splitter"

    handleWidth = Prop(int, qt=("handleWidth", "setHandleWidth"))
    orientation = Prop(object, qt=("orientation", "setOrientation"), coerce=_orientation)
    sizes = Prop(object, qt=("sizes", "setSizes"), coerce=_to_size_list,
                 doc="a list of pane sizes, one per child")

    onMove = Event("splitterMoved", passes_self=True,
                   params=(("position", "integer"), ("index", "integer")),
                   indices=("index",),
                   doc="Fired when the user drags a handle -- not when setSizes "
                       "moves one -- so a caller can tell a size the user chose "
                       "from one it set. index is 1-based.")

    def __init__(self, orientation="vertical"):
        super().__init__(_orientation(orientation))

    def addChild(self, child):
        self.addWidget(child)
        return self

    def addLayout(self, layout):
        widget = QWidget()
        widget.setLayout(layout)
        self.addChild(widget)
        return self

    @method({"factors": "integer[]"}, returns="self",
            doc="How extra room is shared out, one integer per child: a child "
                "with 0 keeps its size when the splitter grows; the others "
                "grow in proportion. setSizes is in pixels; this is the ratio.")
    def setStretchFactors(self, factors):
        for index, factor in enumerate(as_sequence(factors)):
            self.setStretchFactor(index, int(factor))
        return self
