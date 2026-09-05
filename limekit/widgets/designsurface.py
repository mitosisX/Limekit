"""A container whose children are looked at, moved about, and dropped onto,
rather than used.

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

Dropping is the same idea run in reverse. The surface works out *where* a
drop would land -- which container, which slot in its layout -- draws that,
and on release reports it. It never adds, moves or removes a widget itself:
the designer's model does that and rebuilds, so the tree on screen can never
drift from the tree that will be written out.
"""

from PySide6.QtCore import QMimeData, QPoint, QRect, Qt
from PySide6.QtGui import QColor, QDrag, QPainter, QPen
from PySide6.QtWidgets import (QApplication, QBoxLayout, QFormLayout,
                               QGridLayout, QVBoxLayout, QWidget)

from limekit.kernel.bridge.convert import to_lua
from limekit.kernel.bridge.guard import guard
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import method
from limekit.widgets.base import LimeWidget

_SELECTION_COLOUR = "#2979FF"
_INDICATOR_COLOUR = "#FF6D00"

#: A class name from the palette: "ui.Button".
CLASS_MIME = "application/x-limekit-class"
#: A widget already on the surface being moved. The payload is only a token;
#: the surface keeps the real reference while the drag is in flight.
MOVE_MIME = "application/x-limekit-move"


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


# -- where a drop lands -------------------------------------------------------

def _layout_kind(layout):
    """"vbox", "hbox", "grid", "form", or None for anything else."""
    if isinstance(layout, QGridLayout):
        return "grid"
    if isinstance(layout, QFormLayout):
        return "form"
    if isinstance(layout, QBoxLayout):
        direction = layout.direction()
        if direction in (QBoxLayout.Direction.TopToBottom,
                         QBoxLayout.Direction.BottomToTop):
            return "vbox"
        return "hbox"
    return None


def _container_for(surface, hit):
    """The nearest widget at or above `hit` that lays children out.

    Stops at the design child: the surface's own QVBoxLayout must never be
    a target, or a drop beside the design would land outside it.
    """
    widget = hit
    while widget is not None and widget is not surface:
        if _layout_kind(widget.layout()) is not None:
            return widget, widget.layout()
        if widget is surface.getDesignChild():
            break
        widget = widget.parentWidget()
    return None, None


def _is_or_descends_from(widget, ancestor):
    while widget is not None:
        if widget is ancestor:
            return True
        widget = widget.parentWidget()
    return False


def _box_slot(layout, kind, local):
    """1-based insertion index, cutting at each item's midpoint."""
    coordinate = local.y() if kind == "vbox" else local.x()
    for i in range(layout.count()):
        rect = layout.itemAt(i).geometry()
        middle = rect.center().y() if kind == "vbox" else rect.center().x()
        if coordinate < middle:
            return i + 1
    return layout.count() + 1


def _grid_slot(layout, local):
    """1-based (row, column). One past the last row or column extends it."""
    rows, columns = layout.rowCount(), layout.columnCount()
    row, column = rows + 1, columns + 1
    for r in range(rows):
        rect = layout.cellRect(r, 0)
        if rect.isValid() and local.y() <= rect.bottom():
            row = r + 1
            break
    for c in range(columns):
        rect = layout.cellRect(0, c)
        if rect.isValid() and local.x() <= rect.right():
            column = c + 1
            break
    return row, column


def _form_row_item(layout, row):
    for role in (QFormLayout.ItemRole.FieldRole, QFormLayout.ItemRole.SpanningRole,
                 QFormLayout.ItemRole.LabelRole):
        item = layout.itemAt(row, role)
        if item is not None:
            return item
    return None


def _form_slot(layout, local):
    for r in range(layout.rowCount()):
        item = _form_row_item(layout, r)
        if item is not None and local.y() < item.geometry().center().y():
            return r + 1
    return layout.rowCount() + 1


def resolve_drop(surface, position, dragging=None):
    """The container and slot a drop at `position` (surface coords) means.

    Pure with respect to the widget tree: nothing is added, moved or
    selected. Returns None when there is nothing to drop into, or when the
    thing being moved would end up inside itself.
    """
    hit = _deepest_at(surface, position) or surface.getDesignChild()
    if hit is None:
        return None
    container, layout = _container_for(surface, hit)
    if container is None:
        return None
    if dragging is not None and _is_or_descends_from(container, dragging):
        return None

    kind = _layout_kind(layout)
    local = container.mapFrom(surface, position)
    slot = {"target": container, "layout": kind}
    if kind in ("vbox", "hbox"):
        slot["index"] = _box_slot(layout, kind, local)
    elif kind == "grid":
        slot["row"], slot["column"] = _grid_slot(layout, local)
    else:
        slot["index"] = _form_slot(layout, local)
    return slot


def indicator_rect(surface, slot):
    """Where the drop indicator is drawn, in surface coordinates."""
    target = slot["target"]
    layout = target.layout()
    origin = target.mapTo(surface, QPoint(0, 0))
    kind = slot["layout"]
    contents = target.contentsRect()

    if kind in ("vbox", "hbox"):
        index, count = slot["index"], layout.count()
        if count == 0:
            if kind == "vbox":
                return QRect(origin.x() + contents.left(), origin.y() + contents.top(),
                             contents.width(), 3)
            return QRect(origin.x() + contents.left(), origin.y() + contents.top(),
                         3, contents.height())
        if index <= count:
            rect, before = layout.itemAt(index - 1).geometry(), True
        else:
            rect, before = layout.itemAt(count - 1).geometry(), False
        if kind == "vbox":
            y = rect.top() if before else rect.bottom()
            return QRect(origin.x() + rect.left(), origin.y() + y - 1, rect.width(), 3)
        x = rect.left() if before else rect.right()
        return QRect(origin.x() + x - 1, origin.y() + rect.top(), 3, rect.height())

    if kind == "grid":
        r, c = slot["row"] - 1, slot["column"] - 1
        rows, columns = layout.rowCount(), layout.columnCount()
        if r < rows and c < columns:
            cell = layout.cellRect(r, c)
        else:
            # A cell that does not exist yet: sketch one at the edge it
            # would extend.
            cell = QRect(contents.right() - 40, contents.bottom() - 24, 40, 24)
            if r < rows:
                cell.moveTop(layout.cellRect(r, 0).top())
            if c < columns:
                cell.moveLeft(layout.cellRect(0, c).left())
        return cell.translated(origin)

    # form
    index, rows = slot["index"], layout.rowCount()
    if rows == 0:
        return QRect(origin.x() + contents.left(), origin.y() + contents.top(),
                     contents.width(), 3)
    item = _form_row_item(layout, min(index, rows) - 1)
    rect = item.geometry() if item is not None else contents
    y = rect.top() if index <= rows else rect.bottom()
    return QRect(origin.x() + contents.left(), origin.y() + y - 1, contents.width(), 3)


class DesignSurface(LimeWidget, QWidget):
    __lime__ = "ui.DesignSurface"

    def __init__(self):
        super().__init__()
        self._onSelect = None
        self._onDrop = None
        self._onContextMenu = None
        self._selected = None
        self._child = None
        self._dropEnabled = True
        self._pending = None        # slot under the cursor during a drag
        self._dragging = None       # widget being moved, while it is
        self._press = None          # (widget, QPoint) of the last press
        self.setAcceptDrops(True)

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
        self._pending = None
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

    @method({"handler": "fun(drop: table)"}, returns="self",
            doc="Called when a class from the palette, or a placed widget, is "
                "dropped. drop = {kind = 'class'|'move', class|widget, target, "
                "layout = 'vbox'|'hbox'|'grid'|'form', index | row, column}. "
                "The surface changes nothing itself.")
    def setOnDrop(self, handler):
        self._onDrop = guard(handler, widget="DesignSurface", event="onDrop")
        return self

    @method({"handler": "fun(widget: any, x: integer, y: integer)"}, returns="self",
            doc="Called on a right-click with the widget under it (or nil) and "
                "the position in the surface, for popping a menu up at.")
    def setOnContextMenu(self, handler):
        self._onContextMenu = guard(handler, widget="DesignSurface", event="onContextMenu")
        return self

    @method({"enabled": "boolean"}, returns="self",
            doc="Whether drops are accepted. On by default.")
    def setDropEnabled(self, enabled):
        self._dropEnabled = bool(enabled)
        return self

    # -- input: selecting, and starting a move -------------------------------

    def mousePressEvent(self, event):
        # childAt walks the same geometry Qt drew, so what is reported is
        # what the eye picked -- no hit-testing of our own to disagree with.
        position = event.position().toPoint()
        hit = _deepest_at(self, position)

        self._selected = hit
        # The design child itself is never moved: it has nowhere else to go.
        self._press = (hit, position) if hit is not None and hit is not self._child else None
        self.update()

        if self._onSelect is not None:
            self._onSelect(hit)
        if event.button() == Qt.MouseButton.RightButton and self._onContextMenu is not None:
            self._press = None
            self._onContextMenu(hit, position.x(), position.y())
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._press is None or not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        widget, origin = self._press
        moved = (event.position().toPoint() - origin).manhattanLength()
        if moved < QApplication.startDragDistance():
            return

        self._press = None
        self._dragging = widget
        mime = QMimeData()
        mime.setData(MOVE_MIME, str(id(widget)).encode())
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.setPixmap(widget.grab())
        drag.setHotSpot(event.position().toPoint() - widget.mapTo(self, QPoint(0, 0)))
        drag.exec(Qt.DropAction.MoveAction)
        self._dragging = None
        self._pending = None
        self.update()

    def mouseReleaseEvent(self, event):
        self._press = None
        super().mouseReleaseEvent(event)

    # -- input: being dropped on ---------------------------------------------

    def _accepts(self, mime):
        return self._dropEnabled and (mime.hasFormat(CLASS_MIME) or mime.hasFormat(MOVE_MIME))

    def dragEnterEvent(self, event):
        if self._accepts(event.mimeData()):
            event.acceptProposedAction()
            self.dragMoveEvent(event)

    def dragMoveEvent(self, event):
        if not self._accepts(event.mimeData()):
            event.ignore()
            return
        slot = resolve_drop(self, event.position().toPoint(), self._dragging)
        self._pending = slot
        self.update()
        if slot is None:
            event.ignore()
        else:
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self._pending = None
        self.update()

    def dropEvent(self, event):
        mime = event.mimeData()
        self._pending = None
        self.update()
        if not self._accepts(mime):
            event.ignore()
            return
        slot = resolve_drop(self, event.position().toPoint(), self._dragging)
        if slot is None:
            event.ignore()
            return

        if mime.hasFormat(CLASS_MIME):
            drop = {"kind": "class", "class": bytes(mime.data(CLASS_MIME)).decode()}
        elif self._dragging is not None:
            drop = {"kind": "move", "widget": self._dragging}
        else:
            # A move mime from some other surface: there is no widget of
            # ours behind it.
            event.ignore()
            return
        drop.update(slot)
        event.acceptProposedAction()
        self._emit_drop(drop)

    def _emit_drop(self, drop):
        if self._onDrop is None:
            return
        try:
            payload = to_lua(drop)
        except BridgeError:
            payload = drop          # no Lua runtime bound: a Python caller
        self._onDrop(payload)

    # -- painting -------------------------------------------------------------

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._selected is None and self._pending is None:
            return

        painter = QPainter(self)
        if self._selected is not None:
            pen = QPen(QColor(_SELECTION_COLOUR))
            pen.setWidth(2)
            painter.setPen(pen)
            # Mapped through this surface's coordinates, because the selected
            # widget may be nested several layouts deep.
            top_left = self._selected.mapTo(self, self._selected.rect().topLeft())
            painter.drawRect(top_left.x(), top_left.y(),
                             self._selected.width() - 1, self._selected.height() - 1)

        if self._pending is not None:
            colour = QColor(_INDICATOR_COLOUR)
            target = self._pending["target"]
            frame = QRect(target.mapTo(self, QPoint(0, 0)), target.size())
            pen = QPen(colour)
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawRect(frame.adjusted(0, 0, -1, -1))

            rect = indicator_rect(self, self._pending)
            if self._pending["layout"] == "grid":
                fill = QColor(colour)
                fill.setAlpha(40)
                painter.fillRect(rect, fill)
                pen.setWidth(2)
                painter.setPen(pen)
                painter.drawRect(rect.adjusted(0, 0, -1, -1))
            else:
                painter.fillRect(rect, colour)
        painter.end()
