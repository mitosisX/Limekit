import pytest
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QColor
from limekit.kernel.coerce import (
    Icon, Size, Colour, LuaIndex, Enum,
    ALIGNMENTS, CURSORS, SIZE_POLICIES,
)
from limekit.kernel.errors import BridgeError


def test_icon_from_path(qapp):
    assert isinstance(Icon("nonexistent.png"), QIcon)


def test_icon_passes_through_an_existing_icon(qapp):
    original = QIcon()
    assert Icon(original) is original


def test_size_from_pair(qapp):
    assert Size((800, 600)) == QSize(800, 600)


def test_colour_from_hex(qapp):
    assert Colour("#ff0000") == QColor(255, 0, 0)


def test_lua_index_is_one_based():
    assert LuaIndex(1) == 0
    assert LuaIndex(5) == 4


def test_lua_index_rejects_zero():
    with pytest.raises(BridgeError, match="1-indexed"):
        LuaIndex(0)


def test_enum_is_case_insensitive():
    align = Enum(ALIGNMENTS, "alignment")
    assert align("CENTER") == Qt.AlignmentFlag.AlignCenter
    assert align("center") == Qt.AlignmentFlag.AlignCenter


def test_enum_rejects_unknown_and_lists_options():
    align = Enum(ALIGNMENTS, "alignment")
    with pytest.raises(BridgeError) as exc:
        align("sideways")
    assert "sideways" in str(exc.value)
    assert "center" in str(exc.value)


def test_cursor_map_has_no_duplicate_targets_for_openhand():
    """label.py defined 'openhand' twice; the second silently won."""
    assert CURSORS["openhand"] == Qt.CursorShape.OpenHandCursor


def test_wait_cursor_is_actually_a_wait_cursor():
    """label.py mapped 'wait' to ArrowCursor."""
    assert CURSORS["wait"] == Qt.CursorShape.WaitCursor


def test_size_policies_are_complete():
    assert set(SIZE_POLICIES) == {
        "fixed", "expanding", "ignore", "maximum",
        "minimum", "minimumexpanding", "preferred",
    }


# Failure mode tests


def test_icon_rejects_non_icon_non_path(qapp):
    with pytest.raises(BridgeError):
        Icon(12345)


def test_size_rejects_non_numeric_width(qapp):
    with pytest.raises(BridgeError):
        Size(("a", 600))


def test_size_rejects_non_numeric_height(qapp):
    with pytest.raises(BridgeError):
        Size((800, "b"))


def test_colour_rejects_non_numeric_rgb_components(qapp):
    with pytest.raises(BridgeError):
        Colour(("a", "b", "c"))


def test_colour_rejects_unparseable_string(qapp):
    with pytest.raises(BridgeError):
        Colour("not-a-colour")


def test_lua_index_rejects_non_numeric_string(qapp):
    with pytest.raises(BridgeError, match="1-indexed"):
        LuaIndex("abc")


def test_lua_index_rejects_none(qapp):
    with pytest.raises(BridgeError, match="1-indexed"):
        LuaIndex(None)
