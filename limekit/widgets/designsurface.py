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

import math
import os
import sys
import time
import weakref

from PySide6.QtCore import QElapsedTimer, QEvent, QMimeData, QObject, QPoint, QRect, Qt, QTimer
from PySide6.QtGui import (QBrush, QColor, QDrag, QFontMetrics, QPainter,
                           QPalette, QPen, QPixmap)
from PySide6.QtWidgets import (QApplication, QBoxLayout, QFormLayout,
                               QGridLayout, QScrollArea, QSplitter,
                               QTabWidget, QVBoxLayout, QWidget)

from limekit.kernel.bridge.convert import as_sequence, to_lua
from limekit.kernel.bridge.guard import guard
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import method
from limekit.widgets.base import LimeWidget
from limekit.widgets.imagebrowser import IMAGE_MIME

_SELECTION_COLOUR = "#2979FF"
_INDICATOR_COLOUR = "#FF6D00"
_REFUSED_COLOUR = "#E5484D"
_IMAGE_COLOUR = "#16A34A"
# Container outlines: a muted blue rather than grey, so an empty container
# on a white window still reads as a place to drop, in either theme.
_CONTAINER_COLOUR = "#6E8BD8"

# What each way of holding children is called on tags and empty hints.
_KIND_WORDS = {"vbox": "Column", "hbox": "Row", "grid": "Grid", "form": "Form",
               "tab": "Tabs", "splitter": "Splitter", "scroller": "Scroller"}
_FLASH_MS = 700
_HANDLE = 7          # px, the little squares on a selection's edges
_TITLE_H = 28        # px, the mock title bar drawn above the design
# The cursor over each selection handle, and while dragging it.
_HANDLE_CURSORS = {"right": Qt.CursorShape.SizeHorCursor,
                   "bottom": Qt.CursorShape.SizeVerCursor,
                   "corner": Qt.CursorShape.SizeFDiagCursor}
_MARGIN = 36         # px of backdrop around the framed design
_GRID = 16           # px between backdrop dots, and the default snapping step
# The zoom steps zoomIn and zoomOut walk, and the range setZoom allows.
_ZOOM_STEPS = (0.25, 0.33, 0.5, 0.67, 0.75, 0.9, 1.0, 1.1, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0)
_ZOOM_MIN, _ZOOM_MAX = _ZOOM_STEPS[0], _ZOOM_STEPS[-1]
_GUIDE_COLOUR = "#E5376B"
_GUIDE_SNAP = 5      # px on screen within which a resized edge meets a guide
# Far enough off the surface that no scroll position or screen ever shows it.
_OFFSTAGE = QPoint(-100000, -100000)

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
    and the first hit is the topmost. The surface's own overlay covers
    everything and is skipped: it is paint, not part of the design.
    """
    for child in reversed([c for c in widget.children() if isinstance(c, QWidget)]):
        if not child.isVisible() or isinstance(child, _Overlay):
            continue
        if child.geometry().contains(position):
            return _deepest_at(child, position - child.pos()) or child
    return None


class _Overlay(QWidget):
    """A transparent sheet over the whole surface that the selection, drop
    indicator and container outlines are drawn on.

    They used to be drawn in the surface's own paintEvent, which Qt runs
    *before* painting children -- so an opaque widget such as a LineEdit
    covered the outline of its own selection. A sibling raised above the
    design paints after it, and being transparent to the mouse it changes
    nothing about hit-testing.
    """

    def __init__(self, surface):
        super().__init__(surface)
        self._surface = surface
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

    def paintEvent(self, event):
        self._surface._paint_overlay(self)


class _PaintLog(QObject):
    """LIMEKIT_DEBUG_PAINT: a record of what appears on a design surface.

    For a flicker that cannot be reproduced outside the app it happens in
    -- a white box at a surface's top-left, seen in Limer and in no test
    harness. Set the variable to 1 to log to stderr, or to a file path to
    log there. Logged: every top-level window shown, every native window
    handle made, and in a surface's window, each Show, Paint, Move and
    Resize of a widget at least 200x150 -- where it is relative to the
    surface, and what holds it -- but only when that differs from what
    was last logged for the same widget, so a repaint in place is quiet.
    """

    _installed = None
    surfaces = weakref.WeakSet()

    @classmethod
    def install_if_asked(cls, surface):
        target = os.environ.get("LIMEKIT_DEBUG_PAINT")
        if not target:
            return
        cls.surfaces.add(surface)
        if cls._installed is None:
            out = sys.stderr if target == "1" else open(target, "a", encoding="utf-8", buffering=1)
            cls._installed = cls(out)
            QApplication.instance().installEventFilter(cls._installed)

    def __init__(self, out):
        super().__init__()
        self._out = out
        self._start = time.monotonic()
        self._last = {}

    def _write(self, text):
        self._out.write(f"[{(time.monotonic() - self._start) * 1000:9.1f} ms] {text}\n")

    def _surface_for(self, widget):
        window = widget.window()
        for surface in list(self.surfaces):
            if surface.window() is window:
                return surface
        return None

    def eventFilter(self, obj, event):
        try:
            kind = event.type()
            if not isinstance(obj, QWidget):
                return False
            if kind == QEvent.Type.Show and obj.isWindow():
                self._write(f"TOP-LEVEL SHOW {type(obj).__name__} {obj.geometry().getRect()} "
                            f"title={obj.windowTitle()!r}")
            elif kind == QEvent.Type.WinIdChange:
                self._write(f"NATIVE HANDLE {type(obj).__name__} {obj.width()}x{obj.height()} "
                            f"window={obj.isWindow()}")
            elif kind in (QEvent.Type.Show, QEvent.Type.Paint, QEvent.Type.Move, QEvent.Type.Resize):
                if obj.width() < 200 or obj.height() < 150 or obj.isWindow():
                    return False
                surface = self._surface_for(obj)
                if surface is None:
                    return False
                at = obj.mapTo(obj.window(), QPoint(0, 0)) - surface.mapTo(obj.window(), QPoint(0, 0))
                key = (kind, at.x(), at.y(), obj.width(), obj.height())
                if self._last.get(id(obj)) == key:
                    return False
                self._last[id(obj)] = key
                holders, parent = [], obj.parentWidget()
                while parent is not None and len(holders) < 3:
                    holders.append(type(parent).__name__)
                    parent = parent.parentWidget()
                design = "  (the design)" if obj is surface._child else ""
                self._write(f"{kind.name:6} {type(obj).__name__} {obj.width()}x{obj.height()} "
                            f"at surface {at.x()},{at.y()} in {'/'.join(holders)}{design}")
        except RuntimeError:                # deleted under us
            pass
        return False


class _Proxy(QWidget):
    """Holds a zoomed design's place in the surface's layout, and draws it:
    the design, grabbed at its real size, scaled to fit.

    It draws the picture itself rather than leaving the surface to paint
    under it: an app stylesheet gives every QWidget a background, and the
    proxy's own fill then covered the design the surface had drawn.
    """

    def __init__(self, surface):
        super().__init__(surface)
        self._surface = surface
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    def paintEvent(self, event):
        shot = self._surface._design_shot()
        if shot is None:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.drawPixmap(self.rect(), shot)
        painter.end()


def _is_dark(palette):
    return palette.color(QPalette.ColorRole.Window).lightness() < 128


def _chip(painter, anchor, text, fill, ink):
    """A small rounded tag naming something: above `anchor` if there is room,
    else just inside its top-left corner. Uses the painter's current font."""
    metrics = painter.fontMetrics()
    w, h = metrics.horizontalAdvance(text) + 12, metrics.height() + 4
    x, y = anchor.left(), anchor.top() - h - 1
    if y < 0:
        x, y = anchor.left() + 2, anchor.top() + 2
    rect = QRect(x, y, w, h)
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(fill)
    painter.drawRoundedRect(rect, 4, 4)
    painter.setPen(ink)
    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
    painter.restore()
    return rect


def _holds_nothing(widget, kind):
    if kind in ("tab", "splitter"):
        return widget.count() == 0
    if kind == "scroller":
        return widget.widget() is None
    layout = widget.layout()
    return layout is not None and layout.count() == 0


def _make_inert(widget):
    """Take a widget and everything under it out of the mouse's reach, and
    the keyboard's.

    Out of the mouse's reach alone is not enough: a LineEdit in the design
    could still take focus -- when the window is activated, Qt hands focus
    to the first focusable widget it finds -- and a focused line edit
    claims Delete, Ctrl+C and the rest as text editing, so the designer's
    own shortcuts went to a field in the design instead.
    """
    for target in [widget] + widget.findChildren(QWidget):
        target.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        target.setFocusPolicy(Qt.FocusPolicy.NoFocus)


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


def _container_kind(widget):
    """How `widget` holds children in a design -- "vbox", "hbox", "grid",
    "form", "tab", "splitter", "scroller" -- or None if it holds none.

    Only Limekit's own layouts and holders count. A design is built from
    ui.VLayout, ui.Tab and the rest; a composite widget is built from Qt's
    own, on the inside -- a Calendar is a QVBoxLayout of parts, an image
    browser has a QScrollArea in it -- and counting those made a drop on a
    Calendar land *in* the Calendar, and gave it a container's outline.
    """
    layout = widget.layout()
    if isinstance(layout, LimeObject):
        kind = _layout_kind(layout)
        if kind is not None:
            return kind
    if isinstance(widget, LimeObject):
        return _holder_kind(widget)
    return None


def _container_for(surface, hit):
    """The nearest widget at or above `hit` that holds children, and how.

    Returns (widget, kind). Stops at the design child: the surface's own
    QVBoxLayout must never be a target, or a drop beside the design would
    land outside it.
    """
    widget = hit
    while widget is not None and widget is not surface:
        kind = _container_kind(widget)
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
        if widget.isVisible() and _container_kind(widget):
            out.append((widget, surface._rect_in(widget)))
    return out


def resolve_drop(surface, position, dragging=None):
    """The container and slot a drop at `position` (surface coords) means.

    Pure with respect to the widget tree: nothing is added, moved or
    selected. Returns None when there is nothing to drop into, or when the
    thing being moved would end up inside itself.
    """
    child = surface.getDesignChild()
    hit = surface._raw_hit(position) or child
    if hit is None:
        return None
    container, kind = _container_for(surface, hit)
    if container is None:
        return None
    # `dragging` is one widget, or every widget of a multiple selection.
    for moving in (dragging if isinstance(dragging, (list, tuple)) else [dragging]):
        if moving is not None and _is_or_descends_from(container, moving):
            return None

    layout = container.layout()
    # In the design's own coordinates, whatever the zoom: the layouts read
    # their geometry there.
    at = surface._to_design(position)
    local = at if container is child else container.mapFrom(child, at)
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
    return surface._rect_in(slot["target"], _indicator_local(slot))


def _indicator_local(slot):
    """The drop indicator in the target's own coordinates."""
    target = slot["target"]
    layout = target.layout()
    origin = QPoint(0, 0)
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
        self._frameTitle = ""
        self._emptyHint = "Drag widgets here from the palette"
        self._labels = {}           # widget -> "ok · Button", from setWidgetLabel
        self._imageTargets = {}     # widget -> slot name, from setImageTarget
        self._imagePending = None   # (widget, slot, file name) during an image drag
        self._onImageDrop = None
        self._hover = None          # widget under the mouse, outside a drag
        self._cursor = None         # QPoint during a drag over the surface
        # Several widgets selected at once. `_selected` stays the primary --
        # the one with handles, the one Properties shows -- and is always
        # the last of `_selection` when there is one.
        self._selection = []
        self._onSelectionChange = None
        self._marquee = None        # (start QPoint, current QPoint) while drawing one
        self._marqueeBase = []      # what was selected before a Ctrl/Shift marquee
        self._marqueeKeep = (None, [])  # the selection to fall back to if it takes nothing
        self._draggingAll = []      # every widget travelling in a move, the pressed one included
        self._pressedInSelection = False
        self._onResizeSelection = None
        self._resizeSize = None     # (width, height) in design px, while resizing
        self._guides = []           # [(x1, y1, x2, y2)] in surface px, while resizing
        self._guidesEnabled = True
        self._gridSize = _GRID
        self._snapToGrid = False
        # Zoom. Qt draws widgets at one size only, so at any zoom but 1 the
        # design is laid out at its real size on a stage far off the surface,
        # and painted from there, scaled, into a proxy that holds its place
        # in the surface's layout. Every position the mouse gives and every
        # frame drawn goes through _to_design and _rect_in, which at zoom 1
        # are plain coordinate maps.
        self._zoom = 1.0
        self._onZoom = None
        self._shot = None           # the design, grabbed, while zoomed
        self._stage = QWidget(self)
        self._stage.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._stage.move(_OFFSTAGE)
        self._stage.hide()
        self._proxy = _Proxy(self)
        self._proxy.hide()
        self.setAcceptDrops(True)
        # Hover feedback needs moves without a button held.
        self.setMouseTracking(True)
        # Takes focus when clicked, so shortcuts scoped to the canvas --
        # Delete above all -- work after clicking a widget, and only then.
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        # Room around the design for the backdrop, and above it for the mock
        # title bar. The design is centred; when it is larger than the view
        # the layout's minimum size makes an enclosing Scroller scroll.
        layout = QVBoxLayout(self)
        layout.setContentsMargins(_MARGIN, _MARGIN + _TITLE_H, _MARGIN, _MARGIN)
        self._layout = layout

        self._overlay = _Overlay(self)
        self._overlay.raise_()
        _PaintLog.install_if_asked(self)

    def _repaint(self):
        self.update()
        self._proxy.update()
        self._overlay.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._overlay.setGeometry(self.rect())

    # -- where the design is, at any zoom ------------------------------------

    def _natural_size(self, child):
        """The size the surface's centring layout gives the design: its size
        hint, within its minimum and maximum. A fixed-size design is that."""
        return child.sizeHint().expandedTo(child.minimumSize()).boundedTo(child.maximumSize())

    def _place_child(self):
        """Puts the design where the zoom says: in the surface's layout at
        zoom 1, or on the off-surface stage with the proxy holding its
        place, scaled, otherwise. Either way it is placed before this
        returns -- see the note at the end."""
        child = self._child
        for widget in (child, self._proxy):
            if widget is not None:
                self._layout.removeWidget(widget)
        self._shot = None
        if child is None:
            self._proxy.hide()
            self._stage.hide()
            return
        if self._zoom == 1.0:
            self._proxy.hide()
            self._stage.hide()
            if child.parentWidget() is not self:
                child.setParent(self)
            self._layout.addWidget(child, 0, Qt.AlignmentFlag.AlignCenter)
        else:
            size = self._natural_size(child)
            if child.parentWidget() is not self._stage:
                child.setParent(self._stage)
            child.move(0, 0)
            child.resize(size)
            self._stage.resize(size)
            self._stage.show()
            self._proxy.setFixedSize(max(1, round(size.width() * self._zoom)),
                                     max(1, round(size.height() * self._zoom)))
            self._layout.addWidget(self._proxy, 0, Qt.AlignmentFlag.AlignCenter)
            self._proxy.show()
        # Placed now, not on the next turn of the event loop. Added to a
        # layout, a widget is still hidden -- Qt shows it later -- and a
        # layout skips a hidden widget, so the design stayed at (0, 0) until
        # then. The window frame and the selection are drawn from where it
        # is, so any paint in that gap -- a save made one -- drew a white,
        # blue-edged box the size of the design at the surface's top-left,
        # the title bar off the top. Shown first, then laid out, it is in
        # place before anything can paint.
        child.show()
        self._layout.activate()

    def _origin(self):
        """Where the design's top-left corner is drawn, in surface px."""
        if self._child is None:
            return QPoint(0, 0)
        if self._zoom == 1.0:
            return self._child.pos()
        return self._proxy.pos()

    def _design_rect(self):
        """Where the design is drawn, in surface px."""
        if self._child is None:
            return QRect()
        if self._zoom == 1.0:
            return self._child.geometry()
        return self._proxy.geometry()

    def _to_design(self, position):
        """A surface position as a point in the design's own coordinates."""
        # Floor, not int(): int truncates toward zero, and a point half a
        # design pixel left of the design would have landed inside it.
        origin, z = self._origin(), self._zoom
        return QPoint(math.floor((position.x() - origin.x()) / z),
                      math.floor((position.y() - origin.y()) / z))

    def _rect_in(self, widget, local=None):
        """A rectangle in `widget`'s own coordinates -- all of it by default --
        as drawn on the surface, in surface px."""
        local = widget.rect() if local is None else local
        if widget is self._child:
            top = local.topLeft()
        else:
            top = widget.mapTo(self._child, local.topLeft())
        origin, z = self._origin(), self._zoom
        if z == 1.0:
            return QRect(origin + top, local.size())
        return QRect(origin.x() + round(top.x() * z), origin.y() + round(top.y() * z),
                     round(local.width() * z), round(local.height() * z))

    def _raw_hit(self, position):
        """Qt's innermost widget of the design under `position`, the design
        itself where nothing inside it is, or None off the design."""
        child = self._child
        if child is None:
            return None
        at = self._to_design(position)
        if not child.rect().contains(at):
            return None
        return _deepest_at(child, at) or child

    def _design_shot(self):
        """The design, rendered at its real size, for painting zoomed. Kept
        until the design, its zoom or the theme changes."""
        if self._shot is None and self._child is not None:
            self._shot = self._child.grab()
        return self._shot

    def changeEvent(self, event):
        # A theme switch repaints every widget; a grab of the old look would not.
        if event.type() in (QEvent.Type.PaletteChange, QEvent.Type.StyleChange):
            self._shot = None
        super().changeEvent(event)

    # -- zoom ---------------------------------------------------------------

    @method({"factor": "number"}, returns="self",
            doc="Draws the design at this scale -- 1 is its real size -- from 0.25 to 3. "
                "Widgets are not resized: the design is shown smaller or larger, and "
                "selecting, dropping and resizing work at any zoom.")
    def setZoom(self, factor):
        try:
            factor = float(factor)
        except (TypeError, ValueError) as exc:
            raise BridgeError(f"zoom must be a number, got {factor!r}") from exc
        factor = round(min(_ZOOM_MAX, max(_ZOOM_MIN, factor)), 2)
        if factor == self._zoom:
            return self
        self._zoom = factor
        self._hover = None
        self._place_child()
        self._overlay.raise_()
        self._repaint()
        if self._onZoom is not None:
            self._onZoom(factor)
        return self

    @method(returns="number", doc="The zoom the design is drawn at; 1 is its real size.")
    def getZoom(self):
        return self._zoom

    @method(returns="self", doc="The next zoom step up, to at most 3.")
    def zoomIn(self):
        return self.setZoom(next((s for s in _ZOOM_STEPS if s > self._zoom + 1e-9), _ZOOM_MAX))

    @method(returns="self", doc="The next zoom step down, to at least 0.25.")
    def zoomOut(self):
        return self.setZoom(next((s for s in reversed(_ZOOM_STEPS) if s < self._zoom - 1e-9), _ZOOM_MIN))

    @method(returns="self", doc="Back to the design's real size.")
    def resetZoom(self):
        return self.setZoom(1.0)

    @method({"handler": "fun(factor: number)"}, returns="self",
            doc="Called whenever the zoom changes -- by setZoom or by Ctrl+wheel on the surface.")
    def setOnZoomChange(self, handler):
        self._onZoom = guard(handler, widget="DesignSurface", event="onZoomChange")
        return self

    def wheelEvent(self, event):
        """Ctrl+wheel zooms; the wheel alone scrolls, as anywhere else."""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoomIn()
            elif event.angleDelta().y() < 0:
                self.zoomOut()
            event.accept()
            return
        super().wheelEvent(event)

    @method({"child": "any"}, returns="self",
            doc="The widget being designed. Replaces whatever was there, and "
                "deletes it: a designer rebuilds its tree on every change.")
    def setDesignChild(self, child):
        # Replacing the design after an edit made on the canvas must leave
        # the canvas focused, so the next Delete or Ctrl+Z still reaches it.
        focus = QApplication.focusWidget()
        had_focus = focus is not None and (focus is self or self.isAncestorOf(focus))
        if self._child is not None and self._child is not child:
            # The old design is deleted, not just detached. Detached, it
            # became a hidden top-level window -- one more per edit, since a
            # designer rebuilds on every change -- and Qt could show it
            # again: the stray window took activation from the designer and
            # with it every keyboard shortcut.
            old = self._child
            self._layout.removeWidget(old)
            old.hide()
            old.setParent(None)
            old.deleteLater()
        elif self._child is not None:
            self._layout.removeWidget(self._child)

        self._child = child
        self._selected = None
        self._selection = []
        self._pending = None
        self._hover = None
        self._labels = {}
        self._imageTargets = {}
        # A flash still lit from the last edit names a widget of the design
        # just replaced. Left running, it went on drawing a frame for a
        # widget that is no longer on the surface.
        self._flash = None
        self._flashTimer.stop()
        if child is not None:
            _make_inert(child)
        self._place_child()
        self._overlay.raise_()
        if had_focus:
            self.setFocus()
        self._repaint()
        return self

    @method({"title": "string"}, returns="self",
            doc="The text in the mock title bar drawn above the design -- "
                "the title the window will have.")
    def setFrameTitle(self, title):
        self._frameTitle = str(title or "")
        self._repaint()
        return self

    @method({"widget": "any", "label": "string"}, returns="self",
            doc="The name shown on a widget's hover, selection and drag tags, "
                "e.g. 'ok · Button'. Without one the widget's type is shown. "
                "Forgotten when the design child is replaced.")
    def setWidgetLabel(self, widget, label):
        if widget is not None:
            self._labels[widget] = str(label or "")
        return self

    def _label(self, widget):
        """The widget's tag: its label, or else what Limekit calls its class
        ("Table") -- never Qt's ("QTableWidget"), which is not a name a
        design uses."""
        label = self._labels.get(widget)
        if label:
            return label
        lime = getattr(type(widget), "__lime__", None)
        if lime:
            return lime.rsplit(".", 1)[-1]
        return "widget"

    def _design_widget(self, widget):
        """The widget in the design that `widget` is, or is a part of.

        `_deepest_at` finds the innermost Qt widget under the mouse, and for
        a composite widget that is a part the design never made: a Table's
        or a ListBox's viewport, a Scroller's, a Splitter's handle, a Tab's
        page stack, the label a form row makes for itself. Selected,
        hovered or double-clicked, such a part names nothing the designer
        knows -- the tag read "QWidget", and a click on a Table's cells
        selected nothing at all. So the hit climbs to the nearest widget
        that is in the design: one given a label with setWidgetLabel when
        the designer labels its widgets (Limer labels every one), or else
        the nearest Limekit widget. The design child stops the climb.
        """
        labelled = bool(self._labels)
        while widget is not None and widget is not self:
            if widget is self._child:
                return widget
            if (widget in self._labels) if labelled else isinstance(widget, LimeObject):
                return widget
            widget = widget.parentWidget()
        return None

    def _hit(self, position):
        """The design widget under `position`, or None over empty surface."""
        return self._design_widget(self._raw_hit(position))

    @method({"widget": "any", "slot": "string"}, returns="self",
            doc="Marks a widget as taking an image dragged from a "
                "ui.ImageBrowser, into the named slot ('icon', 'image', "
                "'window icon'). Forgotten when the design child is replaced.")
    def setImageTarget(self, widget, slot):
        if widget is not None:
            self._imageTargets[widget] = str(slot or "image")
        return self

    @method({"handler": "fun(widget: any, image: string)"}, returns="self",
            doc="Called when an image from a ui.ImageBrowser is dropped on an "
                "image target, with the widget and the image's path relative "
                "to the browser's root. The surface changes nothing itself.")
    def setOnImageDrop(self, handler):
        self._onImageDrop = guard(handler, widget="DesignSurface", event="onImageDrop")
        return self

    def _image_target_at(self, position):
        """The nearest image target at or above the widget under `position`;
        the design child itself when over its client area or title bar."""
        widget = self._raw_hit(position)
        title = self._title_rect()
        if widget is None and title is not None and title.contains(position):
            widget = self._child
        while widget is not None and widget is not self:
            if widget in self._imageTargets:
                return widget
            if widget is self._child:
                break
            widget = widget.parentWidget()
        return None

    @method({"text": "string"}, returns="self",
            doc="What an empty design shows. Empty text shows nothing.")
    def setEmptyHint(self, text):
        self._emptyHint = str(text or "")
        self._repaint()
        return self

    def _title_rect(self):
        """The mock title bar, in surface coordinates, or None."""
        if self._child is None:
            return None
        g = self._design_rect()
        return QRect(g.left(), g.top() - _TITLE_H, g.width(), _TITLE_H)

    @method({"widget": "any"}, returns="integer, integer",
            doc="The width and height a widget of the design is laid out at, in its "
                "own px -- whatever the zoom. For matching one widget's size to another's.")
    def getWidgetSize(self, widget):
        return widget.width(), widget.height()

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
        self._shot = None
        self._overlay.raise_()
        self._repaint()
        return self

    @method({"widget": "any"}, returns="self",
            doc="Draws the selection outline around a widget.")
    def setSelected(self, widget):
        self._selected = widget
        self._selection = [] if widget is None else [widget]
        self._repaint()
        return self

    @method(returns="any", doc="The selected widget, or nil. With several selected, the primary one.")
    def getSelected(self):
        return self._selected

    @method({"widgets": "any[]"}, returns="self",
            doc="Selects several widgets at once. The last is the primary one: the "
                "one with resize handles, the one getSelected returns.")
    def setSelection(self, widgets):
        items = [w for w in as_sequence(widgets) if w is not None]
        self._selection = items
        self._selected = items[-1] if items else None
        self._repaint()
        return self

    @method(returns="any[]", doc="Every selected widget, the primary one last.")
    def getSelection(self):
        return self._lua_list(self._selection)

    @method({"handler": "fun(widgets: any[])"}, returns="self",
            doc="Called when Ctrl- or Shift-clicking, or dragging a marquee, changes a "
                "selection of several widgets, with all of them, the primary one last. "
                "A plain click still reports through setOnSelect.")
    def setOnSelectionChange(self, handler):
        self._onSelectionChange = guard(handler, widget="DesignSurface", event="onSelectionChange")
        return self

    def _lua_list(self, items):
        try:
            return to_lua(list(items))
        except BridgeError:
            return list(items)      # no Lua runtime bound: a Python caller

    def _announce_selection(self):
        self._repaint()
        if self._onSelectionChange is not None:
            self._onSelectionChange(self._lua_list(self._selection))
        elif self._onSelect is not None:
            self._onSelect(self._selected)

    @method({"size": "integer"}, returns="self",
            doc="The grid step in px -- the backdrop's dots, and what snapping rounds to. 16 by default.")
    def setGridSize(self, size):
        try:
            size = int(size)
        except (TypeError, ValueError) as exc:
            raise BridgeError(f"grid size must be a whole number, got {size!r}") from exc
        self._gridSize = max(2, min(200, size))
        self._repaint()
        return self

    @method(returns="integer", doc="The grid step in px.")
    def getGridSize(self):
        return self._gridSize

    @method({"enabled": "boolean"}, returns="self",
            doc="Whether a resize snaps to the grid. Off by default.")
    def setSnapToGrid(self, enabled):
        self._snapToGrid = bool(enabled)
        return self

    @method(returns="boolean", doc="Whether a resize snaps to the grid.")
    def getSnapToGrid(self):
        return self._snapToGrid

    @method({"enabled": "boolean"}, returns="self",
            doc="Whether a resize shows -- and snaps to -- guide lines where the edge it "
                "pulls meets another widget's edge or matches another widget's size. On by default.")
    def setGuidesEnabled(self, enabled):
        self._guidesEnabled = bool(enabled)
        return self

    @method(returns="boolean", doc="Whether a resize shows and snaps to guide lines.")
    def getGuidesEnabled(self):
        return self._guidesEnabled

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
        try:
            return self._rect_in(self._selected)
        except RuntimeError:                # deleted under us
            return None

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
        self._repaint()
        return self

    def _flash_tick(self):
        if self._flash is None or self._flash[1].elapsed() >= _FLASH_MS:
            self._flash = None
            self._flashTimer.stop()
        self._overlay.update()

    def isFlashing(self):
        return self._flash is not None

    # -- input: selecting, and starting a move -------------------------------

    def _design_widgets(self):
        """Every widget of the design that can be selected, the design itself
        aside: each labelled one -- or, when nothing is labelled, each
        Limekit widget -- that is showing."""
        if self._child is None:
            return []
        labelled = bool(self._labels)
        return [w for w in self._child.findChildren(QWidget)
                if w.isVisible() and ((w in self._labels) if labelled else isinstance(w, LimeObject))]

    def _enclosed(self, rect):
        """The widgets a marquee takes: those wholly inside `rect`, outermost
        only -- a row taken whole takes its buttons with it, and selecting
        both would move or delete each button twice."""
        inside = [w for w in self._design_widgets() if rect.contains(self._rect_in(w))]
        taken = set(inside)

        def outermost(widget):
            holder = self._design_widget(widget.parentWidget())
            while holder is not None and holder is not self._child:
                if holder in taken:
                    return False
                holder = self._design_widget(holder.parentWidget())
            return True

        return [w for w in inside if outermost(w)]

    def mousePressEvent(self, event):
        position = event.position().toPoint()
        left = event.button() == Qt.MouseButton.LeftButton
        right = event.button() == Qt.MouseButton.RightButton
        additive = bool(event.modifiers() & (Qt.KeyboardModifier.ControlModifier
                                             | Qt.KeyboardModifier.ShiftModifier))

        # A press on a handle of the selection starts a resize, not a new
        # selection -- the handle sits on the widget's edge, where the
        # hit-test below would as likely pick the neighbour.
        handle = self._handle_at(position) if left and not additive else None
        if handle is not None:
            self._resizing = (self._selected, handle, position, self._selected.size(),
                              [(w, w.size()) for w in (self._selection or [self._selected])])
            self._resizeRect = self._selection_frame()
            self._resizeSize = (self._selected.width(), self._selected.height())
            self._press = None
            return

        # childAt walks the same geometry Qt drew, so what is reported is
        # what the eye picked -- no hit-testing of our own to disagree with --
        # then climbs out of any part of a widget the design never made.
        hit = self._hit(position)
        # The title bar stands for the window, which is the design child.
        title = self._title_rect()
        if hit is None and title is not None and title.contains(position):
            hit = self._child

        # Ctrl- or Shift-click adds a widget to the selection, or takes it
        # out; on the window or the empty surface it starts a marquee that
        # adds to what is already selected.
        if left and additive:
            self._press = None
            if hit is None or hit is self._child:
                self._marquee = (position, position)
                self._marqueeBase = [w for w in self._selection if w is not self._child]
                self._marqueeKeep = (self._selected, list(self._selection))
                return
            if hit in self._selection:
                self._selection = [w for w in self._selection if w is not hit]
            else:
                self._selection = [w for w in self._selection if w is not self._child] + [hit]
            self._selected = self._selection[-1] if self._selection else None
            self._announce_selection()
            return

        # A press on one of several selected widgets keeps them all: it may
        # be the start of moving them together, or the right-click that
        # deletes them. Released without a drag, a left press selects that
        # one alone.
        if hit is not None and hit in self._selection and len(self._selection) > 1:
            if left:
                self._pressedInSelection = True
                self._press = (hit, position)
                return
            if right and self._onContextMenu is not None:
                self._onContextMenu(hit, position.x(), position.y())
                return

        self._selected = hit
        self._selection = [] if hit is None else [hit]
        # The design child itself is never moved: it has nowhere else to go.
        # A drag that starts on it, or on the empty surface, draws a marquee.
        if left and (hit is None or hit is self._child):
            self._press = None
            self._marquee = (position, position)
            self._marqueeBase = []
            self._marqueeKeep = (hit, list(self._selection))
        else:
            self._press = (hit, position) if hit is not None else None
        self._repaint()

        if self._onSelect is not None:
            self._onSelect(hit)
        if right and self._onContextMenu is not None:
            self._press = None
            self._marquee = None
            self._onContextMenu(hit, position.x(), position.y())
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        position = event.position().toPoint()
        self._marquee = None
        if self._onDoubleClick is not None:
            self._onDoubleClick(self._hit(position), position.x(), position.y())
        super().mouseDoubleClickEvent(event)

    def _snap_length(self, length, start, axis, widget):
        """A resized width or height (design px) adjusted to the nearest guide
        within reach, or else to the grid when snapping. `start` is the
        widget's fixed edge on the surface. Records the guide it used."""
        z = self._zoom
        edge = start + length * z
        best = None                       # (distance, new length, guide)
        if self._guidesEnabled:
            frame = self._selection_frame()
            for other in self._design_widgets():
                if other is widget or _is_or_descends_from(other, widget):
                    continue
                try:
                    r = self._rect_in(other)
                except RuntimeError:
                    continue
                name = self._label(other)
                if axis == "x":
                    lines = [(r.left(), None), (r.right() + 1, None),
                             (start + r.width(), f"width of {name}")]
                else:
                    lines = [(r.top(), None), (r.bottom() + 1, None),
                             (start + r.height(), f"height of {name}")]
                for at, match in lines:
                    distance = abs(at - edge)
                    if distance > _GUIDE_SNAP or at <= start or (best is not None and distance >= best[0]):
                        continue
                    if match is not None:
                        # The same size: a line across the other widget, at its middle.
                        guide = ((r.left(), r.center().y(), r.right(), r.center().y()) if axis == "x"
                                 else (r.center().x(), r.top(), r.center().x(), r.bottom()), match)
                    elif axis == "x":
                        top = min(r.top(), frame.top()) if frame else r.top()
                        bottom = max(r.bottom(), frame.bottom()) if frame else r.bottom()
                        guide = ((at, top - 8, at, bottom + 8), None)
                    else:
                        lft = min(r.left(), frame.left()) if frame else r.left()
                        rgt = max(r.right(), frame.right()) if frame else r.right()
                        guide = ((lft - 8, at, rgt + 8, at), None)
                    best = (distance, (at - start) / z, guide)
        if best is not None:
            self._guides.append(best[2])
            return best[1]
        if self._snapToGrid:
            step = self._gridSize
            return max(step, round(length / step) * step)
        return length

    def _drag_resize(self, position):
        widget, handle, start, size, _ = self._resizing
        z = self._zoom
        width = size.width() + ((position.x() - start.x()) / z if handle in ("right", "corner") else 0)
        height = size.height() + ((position.y() - start.y()) / z if handle in ("bottom", "corner") else 0)
        frame = self._selection_frame()
        self._guides = []
        if frame is not None:
            if handle in ("right", "corner"):
                width = self._snap_length(width, frame.left(), "x", widget)
            if handle in ("bottom", "corner"):
                height = self._snap_length(height, frame.top(), "y", widget)
        width, height = max(8, round(width)), max(8, round(height))
        self._resizeSize = (width, height)
        if frame is not None:
            self._resizeRect = QRect(frame.left(), frame.top(), round(width * z), round(height * z))

    def mouseMoveEvent(self, event):
        position = event.position().toPoint()
        if self._resizing is not None:
            self._drag_resize(position)
            self._overlay.update()
            return
        if self._marquee is not None:
            if event.buttons() & Qt.MouseButton.LeftButton:
                start = self._marquee[0]
                self._marquee = (start, position)
                if (position - start).manhattanLength() >= QApplication.startDragDistance():
                    found = self._enclosed(QRect(start, position).normalized())
                    self._selection = [w for w in self._marqueeBase if w not in found] + found
                    self._selected = self._selection[-1] if self._selection else None
                self._overlay.update()
                return
            self._marquee = None
        if not event.buttons():
            # Over a selection handle, the cursor says which way it resizes.
            handle = self._handle_at(position)
            if handle is not None:
                self.setCursor(_HANDLE_CURSORS[handle])
            else:
                self.unsetCursor()
            hover = self._hit(position)
            if hover is not self._hover:
                self._hover = hover
                self._overlay.update()
            return
        if self._press is None or not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        widget, origin = self._press
        moved = (position - origin).manhattanLength()
        if moved < QApplication.startDragDistance():
            return

        self._press = None
        self._pressedInSelection = False
        self._hover = None
        # One of several selected: they all travel, in the order they are in
        # the design.
        if widget in self._selection and len(self._selection) > 1:
            order = {w: i for i, w in enumerate(self._child.findChildren(QWidget))}
            moving = sorted(self._selection, key=lambda w: order.get(w, 0))
        else:
            moving = [widget]
        self._dragging = widget
        self._draggingAll = moving
        mime = QMimeData()
        mime.setData(MOVE_MIME, str(id(widget)).encode())
        drag = QDrag(self)
        drag.setMimeData(mime)
        frame = self._rect_in(widget)
        grip = QPoint(int((position.x() - frame.x()) / self._zoom),
                      int((position.y() - frame.y()) / self._zoom))
        pixmap, hotspot = self._drag_pixmap(widget, grip, len(moving))
        drag.setPixmap(pixmap)
        drag.setHotSpot(hotspot)
        self._repaint()             # ghost the source before the drag starts
        drag.exec(Qt.DropAction.MoveAction)
        self._dragging = None
        self._draggingAll = []
        self._pending = None
        self._cursor = None
        self._repaint()

    def leaveEvent(self, event):
        self._hover = None
        self._overlay.update()
        super().leaveEvent(event)

    def _drag_pixmap(self, widget, grip, count=1):
        """What follows the cursor during a move: the widget, faded, framed
        in the selection colour, with its name on a tag above it.

        A bare grab of a container is a white rectangle on a white window --
        there is nothing to see moving. The frame and the tag are what make
        it readable. With several widgets moving, the tag says how many.
        Returns (pixmap, hotspot).
        """
        name = self._label(widget) if count == 1 else f"{count} widgets"
        shot = widget.grab()
        dpr = shot.devicePixelRatio()
        size = shot.deviceIndependentSize()
        scale = min(1.0, 260.0 / max(1.0, size.width()))
        w, h = max(24, int(size.width() * scale)), max(16, int(size.height() * scale))
        font = self.font()
        font.setPointSizeF(font.pointSizeF() * 0.85)
        metrics = QFontMetrics(font)
        tag_h = metrics.height() + 6
        pad = 2

        pixmap = QPixmap(int((max(w, metrics.horizontalAdvance(name) + 16) + pad * 2) * dpr),
                         int((h + tag_h + pad * 2) * dpr))
        pixmap.setDevicePixelRatio(dpr)
        pixmap.fill(Qt.GlobalColor.transparent)
        body = QRect(pad, tag_h + pad, w, h)

        painter = QPainter(pixmap)
        painter.setOpacity(0.88)
        painter.fillRect(body, self.palette().color(QPalette.ColorRole.Window))
        painter.drawPixmap(body, shot)
        painter.setOpacity(1.0)
        painter.setPen(QPen(QColor(_SELECTION_COLOUR), 2))
        painter.drawRect(body.adjusted(0, 0, -1, -1))
        painter.setFont(font)
        _chip(painter, QRect(pad, tag_h + pad, w, h), name,
              QColor(_SELECTION_COLOUR), QColor("#FFFFFF"))
        painter.end()
        hotspot = QPoint(int(grip.x() * scale) + pad, int(grip.y() * scale) + tag_h + pad)
        return pixmap, hotspot

    def mouseReleaseEvent(self, event):
        if self._resizing is not None:
            widget, handle, start, size, starts = self._resizing
            final = self._resizeSize
            self._resizing, self._resizeRect, self._resizeSize = None, None, None
            self._guides = []
            self.unsetCursor()
            self._repaint()
            if final is None or final == (size.width(), size.height()):
                return
            # Every selected widget pulled by the same amount, along the
            # handle's own direction only.
            dw = final[0] - size.width() if handle in ("right", "corner") else 0
            dh = final[1] - size.height() if handle in ("bottom", "corner") else 0
            sizes = [{"widget": w, "width": max(8, s.width() + dw), "height": max(8, s.height() + dh)}
                     for w, s in starts]
            if self._onResizeSelection is not None:
                self._onResizeSelection(self._lua_list(sizes))
            elif self._onResize is not None:
                self._onResize(widget, final[0], final[1])
            return
        if self._marquee is not None:
            start, end = self._marquee
            self._marquee = None
            if (end - start).manhattanLength() >= QApplication.startDragDistance():
                if not self._selection:
                    # Nothing enclosed: what was selected when the drag began stays.
                    self._selected, self._selection = self._marqueeKeep
                self._announce_selection()
            self._overlay.update()
            return
        if self._pressedInSelection and self._press is not None:
            # A press on one of several, released where it began: that one alone.
            hit = self._press[0]
            self._pressedInSelection = False
            self._press = None
            self._selected, self._selection = hit, [hit]
            self._repaint()
            if self._onSelect is not None:
                self._onSelect(hit)
            return
        self._press = None
        super().mouseReleaseEvent(event)

    @method({"handler": "fun(sizes: table[])"}, returns="self",
            doc="Called when a selection handle is dragged and released, with "
                "{widget, width, height} for every selected widget -- each pulled "
                "by the same amount. Preferred over setOnResize, which hears only "
                "the primary widget. The surface changes nothing.")
    def setOnResizeSelection(self, handler):
        self._onResizeSelection = guard(handler, widget="DesignSurface", event="onResizeSelection")
        return self

    # -- input: being dropped on ---------------------------------------------

    def _accepts(self, mime):
        return self._dropEnabled and (mime.hasFormat(CLASS_MIME) or mime.hasFormat(MOVE_MIME)
                                      or mime.hasFormat(IMAGE_MIME))

    def _image_drag(self, event):
        """Handles a drag carrying an image. Returns True if it was one."""
        mime = event.mimeData()
        if not mime.hasFormat(IMAGE_MIME) or mime.hasFormat(CLASS_MIME) or mime.hasFormat(MOVE_MIME):
            return False
        self._cursor = event.position().toPoint()
        self._pending = None
        target = self._image_target_at(self._cursor)
        name = bytes(mime.data(IMAGE_MIME)).decode().rsplit("/", 1)[-1]
        self._imagePending = (target, self._imageTargets[target], name) if target is not None else None
        self._overlay.update()
        if target is None:
            event.ignore()
        else:
            event.acceptProposedAction()
        return True

    def dragEnterEvent(self, event):
        if self._accepts(event.mimeData()):
            event.acceptProposedAction()
            self.dragMoveEvent(event)

    def dragMoveEvent(self, event):
        if not self._accepts(event.mimeData()):
            event.ignore()
            return
        if self._image_drag(event):
            return
        self._cursor = event.position().toPoint()
        slot = resolve_drop(self, self._cursor, self._draggingAll or self._dragging)
        self._pending = slot
        self._overlay.update()
        if slot is None:
            event.ignore()
        else:
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self._pending = None
        self._imagePending = None
        self._cursor = None
        self._overlay.update()

    def dropEvent(self, event):
        mime = event.mimeData()
        self._pending = None
        self._imagePending = None
        self._cursor = None
        self._overlay.update()
        if not self._accepts(mime):
            event.ignore()
            return
        if mime.hasFormat(IMAGE_MIME) and not (mime.hasFormat(CLASS_MIME) or mime.hasFormat(MOVE_MIME)):
            target = self._image_target_at(event.position().toPoint())
            if target is None:
                event.ignore()
                return
            event.acceptProposedAction()
            if self._onImageDrop is not None:
                self._onImageDrop(target, bytes(mime.data(IMAGE_MIME)).decode())
            return
        slot = resolve_drop(self, event.position().toPoint(), self._draggingAll or self._dragging)
        if slot is None:
            event.ignore()
            return

        if mime.hasFormat(CLASS_MIME):
            drop = {"kind": "class", "class": bytes(mime.data(CLASS_MIME)).decode()}
        elif self._dragging is not None:
            # `widgets` is everything moving, in design order; `widget` the one held.
            drop = {"kind": "move", "widget": self._dragging,
                    "widgets": list(self._draggingAll or [self._dragging])}
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
        """Under the design: a dotted backdrop, and the window it will be."""
        super().paintEvent(event)
        palette = self.palette()
        dark = _is_dark(palette)
        window = palette.color(QPalette.ColorRole.Window)

        painter = QPainter(self)
        painter.fillRect(self.rect(), window.darker(135) if dark else window.darker(106))
        dot = QColor(palette.color(QPalette.ColorRole.WindowText))
        dot.setAlpha(28 if dark else 34)
        # The dots are the grid: one step apart at the current zoom, and in
        # line with the design's corner, so a size snapped to the grid ends
        # on a dot.
        step = max(1, round(self._gridSize * self._zoom))
        if step >= 4:
            origin = self._origin()
            left, top = event.rect().left(), event.rect().top()
            first_x = left - (left - origin.x()) % step
            first_y = top - (top - origin.y()) % step
            for x in range(first_x, event.rect().right() + 1, step):
                for y in range(first_y, event.rect().bottom() + 1, step):
                    painter.fillRect(x, y, 1, 1, dot)

        title = self._title_rect()
        if title is not None:
            client = self._design_rect()
            frame = title.united(client)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            # A soft shadow: a few widening, fading outlines.
            for spread in range(1, 7):
                shade = QColor(0, 0, 0, (60 if dark else 22) - spread * (8 if dark else 3))
                painter.setPen(QPen(shade, 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(frame.adjusted(-spread, -spread + 1, spread, spread + 2),
                                        6 + spread, 6 + spread)
            painter.setPen(Qt.PenStyle.NoPen)
            bar = window.lighter(112) if dark else window.darker(104)
            painter.setBrush(bar)
            painter.drawRoundedRect(frame, 6, 6)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            painter.fillRect(client, window)

            text = QColor(palette.color(QPalette.ColorRole.WindowText))
            painter.setPen(text)
            painter.drawText(title.adjusted(12, 0, -70, 0),
                             Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                             self._frameTitle)
            # Minimise, maximise, close: drawn as plain glyphs, so the frame
            # reads as "a window" on every OS without pretending to be one.
            glyph = QColor(text)
            glyph.setAlpha(150)
            painter.setPen(QPen(glyph, 1.2))
            cy, right = title.center().y(), title.right() - 14
            painter.drawLine(right - 44, cy, right - 36, cy)
            painter.drawRect(right - 24, cy - 4, 8, 8)
            painter.drawLine(right - 4, cy - 4, right + 4, cy + 4)
            painter.drawLine(right - 4, cy + 4, right + 4, cy - 4)
        painter.end()

    def _paint_overlay(self, sheet):
        """Over the design: what can be dropped into, what the mouse is on,
        what is selected, and -- during a drag -- where the widget is coming
        from, where it will go, and whether it can go there at all."""
        if self._child is None:
            return

        palette = self.palette()
        ink = QColor(palette.color(QPalette.ColorRole.WindowText))
        painter = QPainter(sheet)
        small = self.font()
        small.setPointSizeF(small.pointSizeF() * 0.85)
        painter.setFont(small)

        def frame_of(widget):
            try:
                return self._rect_in(widget)
            except RuntimeError:            # deleted under us
                return None

        layout = self._child.layout()
        if self._emptyHint and layout is not None and layout.count() == 0:
            hint = QColor(ink)
            hint.setAlpha(110)
            painter.setPen(hint)
            painter.drawText(self._design_rect(), Qt.AlignmentFlag.AlignCenter, self._emptyHint)

        # Containers: a dashed outline on every one, and an empty one tinted
        # and labelled, since it has no look of its own to find it by.
        outline = QColor(_CONTAINER_COLOUR)
        outline.setAlpha(170)
        tint = QColor(_CONTAINER_COLOUR)
        tint.setAlpha(22)
        label_ink = QColor(_CONTAINER_COLOUR)
        for widget, frame in container_frames(self):
            if widget is self._child:
                continue
            kind = _container_kind(widget)
            if _holds_nothing(widget, kind):
                painter.fillRect(frame, tint)
                if frame.width() > 60 and frame.height() > 18:
                    painter.setPen(label_ink)
                    painter.drawText(frame, Qt.AlignmentFlag.AlignCenter,
                                     f"{_KIND_WORDS.get(kind, 'Box')} · drop widgets here"
                                     if frame.width() > 170 else _KIND_WORDS.get(kind, "Box"))
            if widget is not self._selected:
                pen = QPen(outline)
                pen.setStyle(Qt.PenStyle.DashLine)
                painter.setPen(pen)
                painter.drawRect(frame.adjusted(0, 0, -1, -1))

        # Hover: a quiet outline and the widget's name, before any click.
        hover = self._hover
        if (hover is not None and self._dragging is None and hover is not self._selected
                and hover is not self._child):
            frame = frame_of(hover)
            if frame is not None:
                colour = QColor(_SELECTION_COLOUR)
                colour.setAlpha(150)
                painter.setPen(QPen(colour, 1))
                painter.drawRect(frame.adjusted(0, 0, -1, -1))
                muted = QColor(_SELECTION_COLOUR)
                muted.setAlpha(170)
                _chip(painter, frame, self._label(hover), muted, QColor("#FFFFFF"))

        if self._flash is not None:
            widget, clock = self._flash
            frame = frame_of(widget)
            if frame is not None:
                fade = max(0.0, 1.0 - clock.elapsed() / _FLASH_MS)
                fill = QColor(_INDICATOR_COLOUR)
                fill.setAlpha(int(110 * fade))
                painter.fillRect(frame, fill)
                pen = QPen(QColor(_INDICATOR_COLOUR))
                pen.setWidth(3)
                painter.setPen(pen)
                painter.drawRect(frame.adjusted(1, 1, -2, -2))

        # The widget being moved: ghosted where it stands, so it is plain
        # which one is travelling and where from.
        for travelling in (self._draggingAll or ([self._dragging] if self._dragging is not None else [])):
            frame = frame_of(travelling)
            if frame is not None:
                veil = QColor(palette.color(QPalette.ColorRole.Window))
                veil.setAlpha(190)
                painter.fillRect(frame, veil)
                hatch = QColor(_SELECTION_COLOUR)
                hatch.setAlpha(70)
                painter.fillRect(frame, QBrush(hatch, Qt.BrushStyle.BDiagPattern))
                pen = QPen(QColor(_SELECTION_COLOUR), 1)
                pen.setStyle(Qt.PenStyle.DashLine)
                painter.setPen(pen)
                painter.drawRect(frame.adjusted(0, 0, -1, -1))

        # The rest of a selection of several: outlined, without handles.
        if self._dragging is None:
            for other in self._selection:
                if other is self._selected or other is self._child:
                    continue
                frame = frame_of(other)
                if frame is not None:
                    painter.setPen(QPen(QColor(_SELECTION_COLOUR), 2))
                    painter.drawRect(frame.adjusted(0, 0, -1, -1))
                    _chip(painter, frame, self._label(other),
                          QColor(_SELECTION_COLOUR), QColor("#FFFFFF"))

        if self._selected is not None and self._dragging is None:
            frame = frame_of(self._selected)
            if frame is not None:
                pen = QPen(QColor(_SELECTION_COLOUR))
                pen.setWidth(2)
                painter.setPen(pen)
                painter.drawRect(frame.adjusted(0, 0, -1, -1))
                for rect in self._handles().values():
                    painter.fillRect(rect, QColor("#FFFFFF"))
                    painter.drawRect(rect.adjusted(0, 0, -1, -1))
                if self._selected is not self._child:
                    _chip(painter, frame, self._label(self._selected),
                          QColor(_SELECTION_COLOUR), QColor("#FFFFFF"))

        if self._resizeRect is not None:
            pen = QPen(QColor(_INDICATOR_COLOUR))
            pen.setWidth(2)
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRect(self._resizeRect.adjusted(0, 0, -1, -1))
            painter.setPen(QColor(_INDICATOR_COLOUR))
            # The size the widget will get, in its own px whatever the zoom.
            w, h = self._resizeSize or (self._resizeRect.width(), self._resizeRect.height())
            matched = [tag for _, tag in self._guides if tag]
            size = f"{w} × {h}" + (f"  = {matched[0]}" if matched else "")
            _chip(painter, self._resizeRect, size, QColor(_INDICATOR_COLOUR), QColor("#FFFFFF"))
            # Guides: where the pulled edge met another widget's edge, or its size.
            guide = QPen(QColor(_GUIDE_COLOUR), 1)
            guide.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(guide)
            for (x1, y1, x2, y2), _ in self._guides:
                painter.drawLine(x1, y1, x2, y2)

        if self._marquee is not None:
            start, end = self._marquee
            if (end - start).manhattanLength() >= QApplication.startDragDistance():
                band = QRect(start, end).normalized()
                fill = QColor(_SELECTION_COLOUR)
                fill.setAlpha(30)
                painter.fillRect(band, fill)
                pen = QPen(QColor(_SELECTION_COLOUR), 1)
                pen.setStyle(Qt.PenStyle.DashLine)
                painter.setPen(pen)
                painter.drawRect(band.adjusted(0, 0, -1, -1))

        if self._imagePending is not None:
            # An image on its way to a widget: the widget lit in green and
            # told what it will get -- "icon <- save.png".
            widget, slot, name = self._imagePending
            frame = frame_of(widget)
            if frame is not None:
                green = QColor(_IMAGE_COLOUR)
                fill = QColor(green)
                fill.setAlpha(40)
                painter.fillRect(frame, fill)
                painter.setPen(QPen(green, 2))
                painter.drawRect(frame.adjusted(1, 1, -2, -2))
                _chip(painter, frame, f"{slot} ← {name}", green, QColor("#FFFFFF"))
        elif self._pending is not None:
            self._paint_drop_target(painter, self._pending)
        elif self._cursor is not None:
            # Over the surface, but nowhere this can go -- say so, rather
            # than leave the user guessing why nothing lights up.
            spot = QRect(self._cursor + QPoint(14, 14), self._cursor + QPoint(15, 15))
            _chip(painter, spot.translated(0, 22), "Can't drop here",
                  QColor(_REFUSED_COLOUR), QColor("#FFFFFF"))
        painter.end()

    def _paint_drop_target(self, painter, slot):
        """The container a drop goes into, tinted and named, and the exact
        slot: a bar with end caps between widgets, or a cell in a grid."""
        colour = QColor(_INDICATOR_COLOUR)
        target = slot["target"]
        frame = self._rect_in(target)
        fill = QColor(colour)
        fill.setAlpha(26)
        painter.fillRect(frame, fill)
        painter.setPen(QPen(colour, 2))
        painter.drawRect(frame.adjusted(1, 1, -2, -2))

        word = _KIND_WORDS.get(slot["layout"], "")
        name = self._label(target) if target is not self._child else "window"
        _chip(painter, frame, f"into {name}" + (f" · {word}" if word else ""),
              colour, QColor("#FFFFFF"))

        rect = indicator_rect(self, slot)
        if slot["layout"] in ("grid", "tab", "scroller"):
            cell = QColor(colour)
            cell.setAlpha(60)
            painter.fillRect(rect, cell)
            painter.setPen(QPen(colour, 2))
            painter.drawRect(rect.adjusted(0, 0, -1, -1))
            return

        # A bar across the gap, thickened to 4px, with a dot at each end so
        # its extent reads even where it crosses a widget's edge.
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        horizontal = rect.width() >= rect.height()
        if horizontal:
            bar = QRect(rect.left(), rect.center().y() - 2, rect.width(), 4)
            ends = (QPoint(bar.left(), bar.center().y()), QPoint(bar.right(), bar.center().y()))
        else:
            bar = QRect(rect.center().x() - 2, rect.top(), 4, rect.height())
            ends = (QPoint(bar.center().x(), bar.top()), QPoint(bar.center().x(), bar.bottom()))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(colour)
        painter.drawRoundedRect(bar, 2, 2)
        for end in ends:
            painter.drawEllipse(end, 5, 5)
        painter.restore()
