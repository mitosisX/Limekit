"""Replacing the design leaves nothing of the old one behind, and
LIMEKIT_DEBUG_PAINT records what appears on a surface."""

import pytest
from PySide6.QtWidgets import QApplication

from limekit.kernel import manifest


@pytest.fixture(scope="module", autouse=True)
def qapp():
    manifest.import_all()
    return QApplication.instance() or QApplication([])


def _surface_with(child):
    from limekit.widgets.designsurface import DesignSurface
    surface = DesignSurface()
    surface.resize(700, 600)
    surface.setDesignChild(child)
    surface.show()
    QApplication.processEvents()
    return surface


def _column(*widgets):
    from limekit.layouts.vlayout import VLayout
    from limekit.widgets.container import Container
    box, layout = Container(), VLayout()
    for widget in widgets:
        layout.addChild(widget)
    box.setLayout(layout)
    box.setFixedSize(400, 300)
    return box


def test_a_flash_does_not_outlive_the_design_it_lit():
    """Flash the root, then rebuild -- a save does exactly that. The flash
    named a widget of the old design, which is no longer on the surface."""
    from limekit.widgets.button import Button
    old = _column(Button("a"))
    surface = _surface_with(old)
    surface.flash(old)
    assert surface.isFlashing()
    surface.setDesignChild(_column(Button("b")))
    assert not surface.isFlashing()


def test_a_flash_on_the_new_design_still_lights(qapp):
    from limekit.widgets.button import Button
    surface = _surface_with(_column(Button("a")))
    fresh = _column(Button("b"))
    surface.setDesignChild(fresh)
    surface.flash(fresh)
    assert surface.isFlashing()


def test_debug_paint_logs_the_design_and_top_level_windows(monkeypatch, tmp_path):
    from limekit.widgets.button import Button
    from limekit.widgets.designsurface import _PaintLog

    log = tmp_path / "paint.log"
    monkeypatch.setenv("LIMEKIT_DEBUG_PAINT", str(log))
    monkeypatch.setattr(_PaintLog, "_installed", None)
    try:
        surface = _surface_with(_column(Button("a")))
        surface.setDesignChild(_column(Button("b")))
        for _ in range(5):
            QApplication.processEvents()
        text = log.read_text(encoding="utf-8")
        assert "TOP-LEVEL SHOW DesignSurface" in text
        assert "(the design)" in text and "at surface" in text
        # A repaint in place is not news: painting the same design again,
        # where it already was, writes nothing more.
        before = log.read_text(encoding="utf-8")
        for _ in range(3):
            surface.getDesignChild().update()
            QApplication.processEvents()
        assert log.read_text(encoding="utf-8") == before
    finally:
        if _PaintLog._installed is not None:
            QApplication.instance().removeEventFilter(_PaintLog._installed)
            _PaintLog._installed._out.close()


def test_without_the_variable_nothing_is_installed(monkeypatch):
    from limekit.widgets.button import Button
    from limekit.widgets.designsurface import _PaintLog

    monkeypatch.delenv("LIMEKIT_DEBUG_PAINT", raising=False)
    monkeypatch.setattr(_PaintLog, "_installed", None)
    _surface_with(_column(Button("a")))
    assert _PaintLog._installed is None
