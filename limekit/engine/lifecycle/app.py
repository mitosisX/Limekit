import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt


# High DPI settings MUST be set before QApplication is created
QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)


class App:
    app = QApplication(sys.argv)

    @classmethod
    def execute(cls):
        try:
            sys.exit(cls.app.exec())
        except Exception as ex:
            from limekit.core.error_handler import handle_exception
            handle_exception(ex, context="Application Event Loop", fatal=True)
