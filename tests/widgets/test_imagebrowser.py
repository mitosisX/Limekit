"""ui.ImageBrowser: a project's images in folders, with names kept unique
across the whole tree so code can refer to an image by name alone."""

import os

import pytest
from PySide6.QtCore import QMimeData, QUrl
from PySide6.QtGui import QColor, QImage
from PySide6.QtWidgets import QApplication

from limekit.kernel import manifest


@pytest.fixture(scope="module", autouse=True)
def qapp():
    manifest.import_all()
    return QApplication.instance() or QApplication([])


def png(path, colour="#ff0000"):
    image = QImage(8, 8, QImage.Format.Format_ARGB32)
    image.fill(QColor(colour))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    image.save(str(path))
    return str(path)


@pytest.fixture
def browser(tmp_path):
    from limekit.widgets.imagebrowser import ImageBrowser
    widget = ImageBrowser()
    widget.setRoot(str(tmp_path / "images"))
    return widget


def files_under(root):
    return sorted(os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/")
                  for d, _, fs in os.walk(root) for f in fs)


def urls(*paths):
    mime = QMimeData()
    mime.setUrls([QUrl.fromLocalFile(p) for p in paths])
    return mime


def test_name_keys_are_lua_identifiers():
    from limekit.widgets.imagebrowser import name_key
    assert name_key("my-logo@2x") == "my_logo_2x"
    assert name_key("2fast") == "_2fast"
    assert name_key("Save") == "Save"
    assert name_key("---") == "image"


def test_set_root_makes_the_folder(tmp_path):
    from limekit.widgets.imagebrowser import ImageBrowser
    root = tmp_path / "new" / "images"
    ImageBrowser().setRoot(str(root))
    assert root.is_dir()


def test_importing_copies_and_keeps_names_unique_across_folders(browser, tmp_path):
    outside = png(tmp_path / "outside" / "logo.png")
    png(tmp_path / "images" / "brand" / "logo.png", "#00ff00")
    assert browser.importFiles([outside]) == 1
    assert files_under(browser.getRoot()) == ["brand/logo.png", "logo_2.png"]
    assert os.path.exists(outside), "importing copies, it does not take the file"


def test_non_images_are_left_out(browser, tmp_path):
    text = tmp_path / "notes.txt"
    text.write_text("hi")
    assert browser.importFiles([str(text)]) == 0
    assert files_under(browser.getRoot()) == []


def test_dropping_an_image_from_the_tree_moves_it(browser, tmp_path):
    root = browser.getRoot()
    icon = png(os.path.join(root, "save.png"))
    os.makedirs(os.path.join(root, "icons"))
    assert browser._take(urls(icon), os.path.join(root, "icons"))
    assert files_under(root) == ["icons/save.png"]


def test_moving_keeps_the_name_when_only_itself_has_it(browser):
    root = browser.getRoot()
    icon = png(os.path.join(root, "a", "save.png"))
    os.makedirs(os.path.join(root, "b"))
    browser._take(urls(icon), os.path.join(root, "b"))
    assert files_under(root) == ["b/save.png"]


def test_a_drop_outside_the_root_is_refused(browser, tmp_path):
    icon = png(tmp_path / "x.png")
    assert not browser._take(urls(icon), str(tmp_path))


def test_new_folder_goes_in_the_folder_shown(browser):
    rel = browser.newFolder("icons")
    assert rel == "icons"
    assert os.path.isdir(os.path.join(browser.getRoot(), "icons"))
    with pytest.raises(Exception):
        browser.newFolder("bad/name")


def test_changes_are_reported_once_and_late(browser, tmp_path):
    seen = []
    browser.setOnChange(lambda: seen.append(1))
    browser.importFiles([png(tmp_path / "o" / "a.png"), png(tmp_path / "o" / "b.png")])
    assert seen == []
    browser._settle.timeout.emit()
    assert seen == [1]


def test_the_breadcrumb_leads_back_up(browser):
    root = browser.getRoot()
    os.makedirs(os.path.join(root, "brand", "dark"))
    browser._crumb("brand/dark")
    assert browser.getCurrentFolder() == "brand/dark"
    assert 'href="brand"' in browser.where.text() and 'href="/"' in browser.where.text()
    browser._crumb("/")
    assert browser.getCurrentFolder() == ""


def test_narrow_shows_icons_and_wide_shows_words(browser):
    from PySide6.QtCore import Qt
    browser.setOrientation("vertical")
    assert all(b.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly for b in browser._buttons)
    browser.setOrientation("horizontal")
    assert all(b.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonTextBesideIcon for b in browser._buttons)


def test_relative_paths_use_forward_slashes(browser):
    path = os.path.join(browser.getRoot(), "brand", "logo.png")
    assert browser.relative(path) == "brand/logo.png"
    assert browser.relative(browser.getRoot()) == ""
