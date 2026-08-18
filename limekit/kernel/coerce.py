"""Coercions that a Prop specifies via `coerce=`.

One shared table per Qt enum, replacing the divergent copies previously
spread across BaseLayout, Label, Window and ComboBox.
"""

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QColor
from PySide6.QtWidgets import QSizePolicy

from limekit.kernel.errors import BridgeError


def Icon(value):
    if isinstance(value, QIcon):
        return value
    try:
        return QIcon(value)
    except (TypeError, ValueError) as exc:
        raise BridgeError(f"expected a QIcon or path string, got {value!r}") from exc


def Size(value):
    if isinstance(value, QSize):
        return value
    try:
        width, height = value
    except (TypeError, ValueError) as exc:
        raise BridgeError(f"expected a {{width, height}} pair, got {value!r}") from exc
    try:
        return QSize(int(width), int(height))
    except (TypeError, ValueError) as exc:
        raise BridgeError(f"expected numeric width and height, got {value!r}") from exc


def Colour(value):
    if isinstance(value, QColor):
        return value
    if isinstance(value, (tuple, list)):
        try:
            return QColor(*(int(c) for c in value))
        except (TypeError, ValueError) as exc:
            raise BridgeError(f"expected numeric RGB components, got {value!r}") from exc
    try:
        color = QColor(value)
        if not color.isValid():
            raise BridgeError(f"invalid color string {value!r}")
        return color
    except (TypeError, ValueError) as exc:
        raise BridgeError(f"expected a color string or RGB tuple, got {value!r}") from exc


def LuaIndex(value):
    """Lua is 1-indexed; Qt is 0-indexed. Convert at the boundary."""
    try:
        index = int(value)
    except (TypeError, ValueError) as exc:
        raise BridgeError(
            f"expected a numeric index, got {value!r} - the Limekit API is 1-indexed"
        ) from exc
    if index < 1:
        raise BridgeError(
            f"index {index} is out of range - the Limekit API is 1-indexed"
        )
    return index - 1


def Enum(mapping, label):
    """Build a case-insensitive string -> Qt enum coercion."""

    def coerce(value):
        if not isinstance(value, str):
            return value
        try:
            return mapping[value.lower()]
        except KeyError:
            options = ", ".join(sorted(mapping))
            raise BridgeError(
                f"unknown {label} {value!r}; expected one of: {options}"
            ) from None

    coerce.__name__ = f"coerce_{label}"
    coerce.options = tuple(sorted(mapping))
    return coerce


def Alignment(value):
    """One alignment name, or several to combine.

    Qt alignments are flags, and combining them is ordinary usage --
    "horizontally centred, at the bottom". `setContentAlignment(...)` on the
    layouts already took several; the Label/Image alignment Props took exactly
    one, so a caller wanting both had no way to say it.

    Accepts "center", or {"hcenter", "bottom"}.
    """
    from limekit.kernel.bridge.convert import as_sequence

    names = [value] if isinstance(value, str) else as_sequence(value)
    if not names:
        raise BridgeError("expected at least one alignment")

    combined = None
    for name in names:
        if not isinstance(name, str):
            combined = name if combined is None else combined | name
            continue
        try:
            flag = ALIGNMENTS[name.lower()]
        except KeyError:
            options = ", ".join(sorted(ALIGNMENTS))
            raise BridgeError(
                f"unknown alignment {name!r}; expected one of: {options}"
            ) from None
        combined = flag if combined is None else combined | flag
    return combined


ALIGNMENTS = {
    "left": Qt.AlignmentFlag.AlignLeft,
    "right": Qt.AlignmentFlag.AlignRight,
    "top": Qt.AlignmentFlag.AlignTop,
    "bottom": Qt.AlignmentFlag.AlignBottom,
    "center": Qt.AlignmentFlag.AlignCenter,
    "hcenter": Qt.AlignmentFlag.AlignHCenter,
    "vcenter": Qt.AlignmentFlag.AlignVCenter,
    "justify": Qt.AlignmentFlag.AlignJustify,
    "baseline": Qt.AlignmentFlag.AlignBaseline,
    "leading": Qt.AlignmentFlag.AlignLeading,
    "trailing": Qt.AlignmentFlag.AlignTrailing,
}

CURSORS = {
    "arrow": Qt.CursorShape.ArrowCursor,
    "uparrow": Qt.CursorShape.UpArrowCursor,
    "wait": Qt.CursorShape.WaitCursor,
    "busy": Qt.CursorShape.BusyCursor,
    "cross": Qt.CursorShape.CrossCursor,
    "ibeam": Qt.CursorShape.IBeamCursor,
    "sizever": Qt.CursorShape.SizeVerCursor,
    "sizehor": Qt.CursorShape.SizeHorCursor,
    "sizebdiag": Qt.CursorShape.SizeBDiagCursor,
    "sizefdiag": Qt.CursorShape.SizeFDiagCursor,
    "sizeall": Qt.CursorShape.SizeAllCursor,
    "blank": Qt.CursorShape.BlankCursor,
    "splitv": Qt.CursorShape.SplitVCursor,
    "splith": Qt.CursorShape.SplitHCursor,
    "pointinghand": Qt.CursorShape.PointingHandCursor,
    "forbidden": Qt.CursorShape.ForbiddenCursor,
    "whatsthis": Qt.CursorShape.WhatsThisCursor,
    "openhand": Qt.CursorShape.OpenHandCursor,
    "closedhand": Qt.CursorShape.ClosedHandCursor,
    "dragcopy": Qt.CursorShape.DragCopyCursor,
    "dragmove": Qt.CursorShape.DragMoveCursor,
    "draglink": Qt.CursorShape.DragLinkCursor,
    "custom": Qt.CursorShape.CustomCursor,
}

DOCK_AREAS = {
    "left": Qt.DockWidgetArea.LeftDockWidgetArea,
    "right": Qt.DockWidgetArea.RightDockWidgetArea,
    "top": Qt.DockWidgetArea.TopDockWidgetArea,
    "bottom": Qt.DockWidgetArea.BottomDockWidgetArea,
    "all": Qt.DockWidgetArea.AllDockWidgetAreas,
    "none": Qt.DockWidgetArea.NoDockWidgetArea,
}

TOOLBAR_AREAS = {
    "left": Qt.ToolBarArea.LeftToolBarArea,
    "right": Qt.ToolBarArea.RightToolBarArea,
    "top": Qt.ToolBarArea.TopToolBarArea,
    "bottom": Qt.ToolBarArea.BottomToolBarArea,
}

ORIENTATIONS = {
    "horizontal": Qt.Orientation.Horizontal,
    "vertical": Qt.Orientation.Vertical,
}

SIZE_POLICIES = {
    "fixed": QSizePolicy.Policy.Fixed,
    "expanding": QSizePolicy.Policy.Expanding,
    "ignore": QSizePolicy.Policy.Ignored,
    "maximum": QSizePolicy.Policy.Maximum,
    "minimum": QSizePolicy.Policy.Minimum,
    "minimumexpanding": QSizePolicy.Policy.MinimumExpanding,
    "preferred": QSizePolicy.Policy.Preferred,
}

Alignment.options = tuple(sorted(ALIGNMENTS))
