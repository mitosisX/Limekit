import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt


class App:
    app = QApplication(sys.argv)
    # app = None

    # The commented method below prevents the program from closing once all windows
    # have been closed; the programs runs in the background
    # app.setQuitOnLastWindowClosed(False)

    # Start the mainloop
    @classmethod
    def execute(cls):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)

        App.app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        App.app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

        # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        try:
            sys.exit(cls.app.exec())
        except Exception as ex:
            print(ex)
