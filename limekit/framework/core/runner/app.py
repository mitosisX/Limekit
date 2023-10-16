import sys

from PySide6.QtWidgets import QApplication


class App:
    app = QApplication([])
    # app = None

    # The commented method below prevents the program from closing once all windows
    # have been closed; the programs runs in the background
    # app.setQuitOnLastWindowClosed(False)

    # Start the mainloop
    @classmethod
    def execute(cls):
        try:
            sys.exit(cls.app.exec())
        except Exception as ex:
            print(ex)
