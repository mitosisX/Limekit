import sys
from PySide6.QtWidgets import QApplication


class App:
    app = QApplication([])

    # The commented method below prevents the program from closing once all windows
    # have been closed; the programs runs in the background
    # app.setQuitOnLastWindowClosed(False)

    # Start the mainloop
    @staticmethod
    def execute():
        sys.exit(App.app.exec())
