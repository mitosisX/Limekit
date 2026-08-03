import os


def test_offscreen_platform_is_set():
    assert os.environ["QT_QPA_PLATFORM"] == "offscreen"


def test_qapplication_available(qapp):
    from PySide6.QtWidgets import QApplication
    assert isinstance(qapp, QApplication)


def test_declared_dependencies_are_importable():
    """Every module limekit imports at runtime must be installable."""
    import importlib
    for mod in ("PySide6", "lupa", "playsound", "psutil", "emoji"):
        importlib.import_module(mod)
