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

from PySide6.QtCore import QElapsedTimer, QMimeData, QPoint, QRect, Qt, QTimer
from PySide6.QtGui import QColor, QDrag, QPainter, QPen
from PySide6.QtWidgets import (QApplication, QBoxLayout, QFormLayout,
                               QGridLayout, QScrollArea, QSplitter,
                               QTabWidget, QVBoxLayout, QWidget)

from limekit.kernel.bridge.convert import to_lua
from limekit.kernel.bridge.guard import guard
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import method
from limekit.widgets.base import LimeWidget

_SELECTION_COLOUR = "#2979FF"
_INDICATOR_COLOUR = "#FF6D00"
_CONTAINER_COLOUR = "#9E9E9E"
_FLASH_MS = 700
_HANDLE = 7          # px, the little squares on a selection's edges

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


def _holder_kind(widget):
    """Widgets that hold children without a QLayout: "tab", "splitter",
    "scroller", or None. A drop on one of these means a new page, pane or
    content rather than a slot in a layout."""
    if isinstance(widget, QTabWidget):
        return "tab"
    if isinstance(widget, QSplitter):
        return "splitter"
    if isinstance(widget, QScrollArea):
        return "scroller"
    return None


def _container_for(surface, hit):
    """The nearest widget at or above `hit` that holds children, and how.

    Returns (widget, kind). Stops at the design child: the surface's own
    QVBoxLayout must never be a target, or a drop beside the design would
    land outside it.
    """
    widget = hit
    while widget is not None and widget is not surface:
        kind = _layout_kind(widget.layout()) or _holder_kind(widget)
        if kind is not None:
            return widget, kind
        if widget is surface.getDesignChild():
            break
        widget = widget.parentWidget()
    return None, None


def _tab_slot(tab, local):
    """1-based page index. Over the tab bar, the tab under the cursor;
    anywhere else, a new page at the end."""
    bar = tab.tabBar()
    if bar.geometry().contains(local):
        at = bar.mapFrom(tab, local)
        horizontal = tab.tabPosition() in (QTabWidget.TabPosition.North,
                                           QTabWidget.TabPosition.South)
        for i in range(bar.count()):
            rect = bar.tabRect(i)
            if horizontal and at.x() < rect.center().x():
                return i + 1
            if not horizontal and at.y() < rect.center().y():
                return i + 1
    return tab.count() + 1


def _splitter_slot(splitter, local):
    vertical = splitter.orientation() == Qt.Orientation.Vertical
    coordinate = local.y() if vertical else local.x()
    for i in range(splitter.count()):
        rect = splitter.widget(i).geometry()
        middle = rect.center().y() if vertical else rect.center().x()
        if coordinate < middle:
            return i + 1
    return splitter.count() + 1


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


def container_frames(surface):
    """(widget, rect) for every container in the design, in surface coords.

    Drawn as dashed outlines so that a container -- which has no look of
    its own, and an empty one has no size to speak of -- can be seen, and
    seen to be the thing a drop will land in.
    """
    child = surface.getDesignChild()
    if child is None:
        return []
    out = []
    for widget in [child] + child.findChildren(QWidget):
        if widget.isVisible() and (_layout_kind(widget.layout()) or _holder_kind(widget)):
            out.append((widget, QRect(widget.mapTo(surface, QPoint(0, 0)), widget.size())))
    return out


def resolve_drop(surface, position, dragging=None):
    """The container and slot a drop at `position` (surface coords) means.

    Pure with respect to the widget tree: nothing is added, moved or
    selected. Returns None when there is nothing to drop into, or when the
    thing being moved would end up inside itself.
    """
    hit = _deepest_at(surface, position) or surface.getDesignChild()
    if hit is None:
        return None
    container, kind = _container_for(surface, hit)
    if container is None:
        return None
    if dragging is not None and _is_or_descends_from(container, dragging):
        return None

    layout = container.layout()
    local = container.mapFrom(surface, position)
    slot = {"target": container, "layout": kind}
    if kind in ("vbox", "hbox"):
        slot["index"] = _box_slot(layout, kind, local)
    elif kind == "grid":
        slot["row"], slot["column"] = _grid_slot(layout, local)
    elif kind == "form":
        slot["index"] = _form_slot(layout, local)
    elif kind == "tab":
        slot["index"] = _tab_slot(container, local)
    elif kind == "splitter":
        slot["index"] = _splitter_slot(container, local)
    else:
        slot["index"] = 1
    return slot


def indicator_rect(surface, slot):
    """Where the drop indicator is drawn, in surface coordinates."""
    target = slot["target"]
    layout = target.layout()
    origin = target.mapTo(surface, QPoint(0, 0))
    kind = slot["layout"]
    contents = target.contentsRect()

    if kind in ("tab", "scroller"):
        return QRect(origin, target.size()).adjusted(1, 1, -2, -2)

    if kind == "splitter":
        index, count = slot["index"], target.count()
        vertical = target.orientation() == Qt.Orientation.Vertical
        if count == 0:
            if vertical:
                return QRect(origin.x() + contents.left(), origin.y() + contents.top(),
                             contents.width(), 3)
            return QRect(origin.x() + contents.left(), origin.y() + contents.top(),
                         3, contents.height())
        if index <= count:
            rect, before = target.widget(index - 1).geometry(), True
        else:
            rect, before = target.widget(count - 1).geometry(), False
        if vertical:
            y = rect.top() if before else rect.bottom()
            return QRect(origin.x() + rect.left(), origin.y() + y - 1, rect.width(), 3)
        x = rect.left() if before else rect.right()
        return QRect(origin.x() + x - 1, origin.y() + rect.top(), 3, rect.height())

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
        self._onResize = None
        self._onDoubleClick = None
        self._resizing = None       # (widget, handle, start QPoint, start QSize)
        self._resizeRect = None     # live outline while resizing
        self._flash = None          # (widget, QElapsedTimer) while lit
        self._flashTimer = QTimer(self)
        self._flashTimer.setInterval(30)
        self._flashTimer.timeout.connect(self._flash_tick)
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

    @method({"handler": "fun(widget: any, width: integer, height: integer)"}, returns="self",
            doc="Called when a selection handle is dragged and released, with "
                "the size the widget was pulled to. The surface changes nothing.")
    def setOnResize(self, handler):
        self._onResize = guard(handler, widget="DesignSurface", event="onResize")
        return self

    @method({"handler": "fun(widget: any, x: integer, y: integer)"}, returns="self",
            doc="Called on a double-click with the widget under it, or nil.")
    def setOnDoubleClick(self, handler):
        self._onDoubleClick = guard(handler, widget="DesignSurface", event="onDoubleClick")
        return self

    def _selection_frame(self):
        if self._selected is None or self._selected is self._child:
            return None
        return QRect(self._selected.mapTo(self, QPoint(0, 0)), self._selected.size())

    def _handles(self):
        """{name: QRect} for the three handles that make sense in a layout:
        a widget's minimum width, its minimum height, or both."""
        frame = self._selection_frame()
        if frame is None:
            return {}
        h = _HANDLE
        return {
            "right": QRect(frame.right() - h // 2, frame.center().y() - h // 2, h, h),
            "bottom": QRect(frame.center().x() - h // 2, frame.bottom() - h // 2, h, h),
            "corner": QRect(frame.right() - h // 2, frame.bottom() - h // 2, h, h),
        }

    def _handle_at(self, position):
        for name, rect in self._handles().items():
            if rect.adjusted(-2, -2, 2, 2).contains(position):
                return name
        return None

    @method({"widget": "any"}, returns="self",
            doc="Lights a widget up briefly -- the one just added, moved or "
                "changed, or the container something was just removed from.")
    def flash(self, widget):
        if widget is None:
            return self
        clock = QElapsedTimer()
        clock.start()
        self._flash = (widget, clock)
        self._flashTimer.start()
        self.update()
        return self

    def _flash_tick(self):
        if self._flash is None or self._flash[1].elapsed() >= _FLASH_MS:
            self._flash = None
            self._flashTimer.stop()
        self.update()

    def isFlashing(self):
        return self._flash is not None

    # -- input: selecting, and starting a move -------------------------------

    def mousePressEvent(self, event):
        position = event.position().toPoint()

        # A press on a handle of the selection starts a resize, not a new
        # selection -- the handle sits on the widget's edge, where the
        # hit-test below would as likely pick the neighbour.
        handle = self._handle_at(position) if event.button() == Qt.MouseButton.LeftButton else None
        if handle is not None:
            self._resizing = (self._selected, handle, position, self._selected.size())
            self._resizeRect = self._selection_frame()
            self._press = None
            return

        # childAt walks the same geometry Qt drew, so what is reported is
        # what the eye picked -- no hit-testing of our own to disagree with.
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

    def mouseDoubleClickEvent(self, event):
        position = event.position().toPoint()
        if self._onDoubleClick is not None:
            self._onDoubleClick(_deepest_at(self, position), position.x(), position.y())
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing is not None:
            widget, handle, start, size = self._resizing
            delta = event.position().toPoint() - start
            width = size.width() + (delta.x() if handle in ("right", "corner") else 0)
            height = size.height() + (delta.y() if handle in ("bottom", "corner") else 0)
            frame = self._selection_frame()
            if frame is not None:
                self._resizeRect = QRect(frame.topLeft(), frame.size())
                self._resizeRect.setWidth(max(8, width))
                self._resizeRect.setHeight(max(8, height))
            self.update()
            return
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
        if self._resizing is not None:
            widget, handle, start, size = self._resizing
            rect = self._resizeRect
            self._resizing, self._resizeRect = None, None
            self.update()
            if rect is not None and self._onResize is not None and rect.size() != size:
                self._onResize(widget, rect.width(), rect.height())
            return
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
        if self._child is None:
            return

        painter = QPainter(self)
        pen = QPen(QColor(_CONTAINER_COLOUR))
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        for widget, frame in container_frames(self):
            if widget is not self._selected:
                painter.drawRect(frame.adjusted(0, 0, -1, -1))

        if self._flash is not None:
            widget, clock = self._flash
            try:
                frame = QRect(widget.mapTo(self, QPoint(0, 0)), widget.size())
            except RuntimeError:            # deleted under us
                frame = None
            if frame is not None:
                fade = max(0.0, 1.0 - clock.elapsed() / _FLASH_MS)
                fill = QColor(_INDICATOR_COLOUR)
                fill.setAlpha(int(110 * fade))
                painter.fillRect(frame, fill)
                pen = QPen(QColor(_INDICATOR_COLOUR))
                pen.setWidth(3)
                painter.setPen(pen)
                painter.drawRect(frame.adjusted(1, 1, -2, -2))

        if self._selected is not None:
            pen = QPen(QColor(_SELECTION_COLOUR))
            pen.setWidth(2)
            painter.setPen(pen)
            # Mapped through this surface's coordinates, because the selected
            # widget may be nested several layouts deep.
            top_left = self._selected.mapTo(self, self._selected.rect().topLeft())
            painter.drawRect(top_left.x(), top_left.y(),
                             self._selected.width() - 1, self._selected.height() - 1)
            for rect in self._handles().values():
                painter.fillRect(rect, QColor("#FFFFFF"))
                painter.drawRect(rect.adjusted(0, 0, -1, -1))

        if self._resizeRect is not None:
            pen = QPen(QColor(_INDICATOR_COLOUR))
            pen.setWidth(2)
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRect(self._resizeRect.adjusted(0, 0, -1, -1))

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
