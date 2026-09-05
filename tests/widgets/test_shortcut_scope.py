"""A shortcut can be told to listen only inside its parent."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from limekit.kernel import manifest


@pytest.fixture(scope="module", autouse=True)
def qapp():
    manifest.import_all()
    return QApplication.instance() or QApplication([])


def test_scope_maps_to_qt_context(qapp):
    from limekit.widgets.container import Container
    from limekit.widgets.shortcut import KeyboardShortcut
    box = Container()
    shortcut = KeyboardShortcut(box, "Ctrl+Z")
    assert shortcut.context() == Qt.ShortcutContext.WindowShortcut
    shortcut.setScope("widget")
    assert shortcut.context() == Qt.ShortcutContext.WidgetWithChildrenShortcut
    shortcut.setScope("application")
    assert shortcut.context() == Qt.ShortcutContext.ApplicationShortcut


def test_combobox_index_is_one_based(qapp):
    from limekit.widgets.combobox import ComboBox
    combo = ComboBox(["a", "b", "c"])
    combo.setCurrentIndex(2)
    assert combo.getText() == "b"
    assert combo.getCurrentIndex() == 2
    combo.setCurrentIndex(0)
    assert combo.getCurrentIndex() == 0
