"""The palette offers only what builds, and hands it over as a drag."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from limekit.kernel import manifest


@pytest.fixture(scope="module", autouse=True)
def qapp():
    manifest.import_all()
    return QApplication.instance() or QApplication([])


def item_named(palette, text):
    return next(palette.list.item(i) for i in range(palette.list.count())
                if palette.list.item(i).text() == text)


def test_every_class_offered_is_buildable_and_a_widget(qapp):
    from limekit.services.inspect import buildable_classes
    from limekit.widgets.widgetpalette import palette_classes
    buildable = {f"ui.{n}" for n in buildable_classes()}
    offered = palette_classes()
    assert offered
    assert set(offered) <= buildable
    assert "ui.Button" in offered
    assert "ui.VLayout" not in offered          # layouts are not widgets
    assert "ui.Window" not in offered           # windows do not go in layouts


def test_every_offered_class_has_a_group(qapp):
    from limekit.widgets.widgetpalette import grouped, palette_classes
    listed = [cls for _, classes in grouped() for cls in classes]
    assert sorted(listed) == palette_classes()


def test_filter_narrows_the_visible_items(qapp):
    from limekit.widgets.widgetpalette import WidgetPalette
    palette = WidgetPalette()
    palette.setFilter("butt")
    visible = [palette.list.item(i).text() for i in range(palette.list.count())
               if not palette.list.item(i).isHidden()]
    assert visible
    assert all("butt" in v.lower() or v in ("Inputs",) for v in visible)
    palette.setFilter("")
    assert not item_named(palette, "Label").isHidden()


def test_double_click_picks_the_class(qapp):
    from limekit.widgets.widgetpalette import WidgetPalette
    palette = WidgetPalette()
    picked = []
    palette.setOnPick(lambda cls: picked.append(cls))
    palette.list.itemDoubleClicked.emit(item_named(palette, "Button"))
    assert picked == ["ui.Button"]


def test_mime_data_carries_the_class(qapp):
    from limekit.widgets.designsurface import CLASS_MIME
    from limekit.widgets.widgetpalette import WidgetPalette
    palette = WidgetPalette()
    mime = palette.list.mimeData([item_named(palette, "Label")])
    assert bytes(mime.data(CLASS_MIME)).decode() == "ui.Label"


def test_headers_cannot_be_picked_or_dragged(qapp):
    from limekit.widgets.widgetpalette import WidgetPalette
    palette = WidgetPalette()
    header = palette.list.item(0)
    assert header.data(Qt.ItemDataRole.UserRole) is None
    assert not (header.flags() & Qt.ItemFlag.ItemIsSelectable)
    assert not (header.flags() & Qt.ItemFlag.ItemIsDragEnabled)


def test_every_widget_the_groups_name_is_offered(qapp):
    """GROUPS names widgets by hand. One that builds but was left off the
    palette -- Spinner, DoubleSpinner and ProgressBar were, because they
    have no __init__ of their own -- could never be dragged onto a design."""
    from limekit.widgets.widgetpalette import GROUPS, palette_classes
    offered = set(palette_classes())
    unbuildable = {"GifPlayer"}         # needs a file to play
    missing = [n for _, names in GROUPS for n in names
               if f"ui.{n}" not in offered and n not in unbuildable]
    assert missing == []
