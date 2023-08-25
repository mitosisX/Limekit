from PySide6.QtWidgets import QMainWindow
from limekit.framework.handle.plugins.base_plugin import BasePlugin


class Plugin2(BasePlugin):
    def __init__(self):
        super().__init__()

    def reverse(self, text):
        return text[::-1]

    def change(self, win):
        win.setWindowTitle("Plugin changed this")
