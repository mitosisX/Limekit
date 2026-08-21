"""A container whose children are looked at rather than used.

A visual designer shows real widgets -- that is the whole point of building
one for a framework with 63 of them -- but a real button pressed is a button
doing its job, not a button being selected. Something has to make the
difference.

The usual answer is an event filter that swallows input. Qt has a smaller
one: `WA_TransparentForMouseEvents` makes a widget invisible to the mouse
without changing how it draws, so every click falls through to the surface
underneath, which then asks Qt what was under the cursor. No filtering, no
guessing, and hit-testing that agrees with what is on screen because Qt did
it.

The attribute has to be applied to the whole subtree: a click landing on a
child of a child would otherwise stop there.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QVBoxLayout, QWidget

from limekit.kernel.bridge.guard import guard
from limekit.kernel.declarative import LimeObject
from limekit.kernel.spec import method
from limekit.widgets.base import LimeWidget

_SELECTION_COLOUR = "#2979FF"


def _deepest_at(widget, position):
    """The innermost visible child of `widget` containing `position`.

    `QWidget.childAt` cannot be used here, which is worth writing down
    because it looks like exactly the right function. It skips any widget
    with WA_TransparentForMouseEvents -- which is every widget in a design,
    by construction -- so it reports the container and never the button
    inside it. The attribute that stops a design reacting is the same
    attribute that hides it from Qt's own hit test.

    Later children are drawn over earlier ones, so the search runs backwards
    and the first hit is the topmost.
    """
    for child in reversed([c for c in widget.children() if isinstance(c, QWidget)]):
        if not child.isVisible():
            continue
        if child.geometry().contains(position):
            return _deepest_at(child, position - child.pos()) or child
    return None


def _make_inert(widget):
    """Take a widget and everything under it out of the mouse's reach."""
    widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
    for child in widget.findChildren(QWidget):
        child.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)


class DesignSurface(LimeWidget, QWidget):
    __lime__ = "ui.DesignSurface"

    def __init__(self):
        super().__init__()
        self._onSelect = None
        self._selected = None
        self._child = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._layout = layout

    @method({"child": "any"}, returns="self",
            doc="The widget being designed. Replaces whatever was there.")
    def setDesignChild(self, child):
        if self._child is not None:
            self._layout.removeWidget(self._child)
            self._child.setParent(None)

        self._child = child
        self._selected = None
        if child is not None:
            self._layout.addWidget(child)
            _make_inert(child)
        self.update()
        return self

    @method(returns="any", doc="The widget being designed, or nil.")
    def getDesignChild(self):
        return self._child

    @method(returns="self",
            doc="Re-applies design mode after the tree has been added to.")
    def refresh(self):
        """Call after building more widgets into the design.

        A widget created later has not been made inert, and a single
        interactive widget in the middle of a design is worse than none --
        clicking it does something the designer never intended and the
        selection silently fails to move.
        """
        if self._child is not None:
            _make_inert(self._child)
        self.update()
        return self

    @method({"widget": "any"}, returns="self",
            doc="Draws the selection outline around a widget.")
    def setSelected(self, widget):
        self._selected = widget
        self.update()
        return self

    @method(returns="any", doc="The selected widget, or nil.")
    def getSelected(self):
        return self._selected

    @method({"handler": "fun(widget: any)"}, returns="self",
            doc="Called with the widget under a click, or nil for empty space.")
    def setOnSelect(self, handler):
        self._onSelect = guard(handler, widget="DesignSurface", event="onSelect")
        return self

    # -- input -------------------------------------------------------------

    def mousePressEvent(self, event):
        # childAt walks the same geometry Qt drew, so what is reported is
        # what the eye picked -- no hit-testing of our own to disagree with.
        position = event.position().toPoint()
        hit = _deepest_at(self, position)

        self._selected = hit
        self.update()

        if self._onSelect is not None:
            self._onSelect(hit)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._selected is None:
            return

        painter = QPainter(self)
        pen = QPen(QColor(_SELECTION_COLOUR))
        pen.setWidth(2)
        painter.setPen(pen)

        # Mapped through this surface's coordinates, because the selected
        # widget may be nested several layouts deep.
        top_left = self._selected.mapTo(self, self._selected.rect().topLeft())
        painter.drawRect(top_left.x(), top_left.y(),
                         self._selected.width() - 1, self._selected.height() - 1)
        painter.end()
