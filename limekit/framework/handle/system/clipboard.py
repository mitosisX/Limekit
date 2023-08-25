# clipboard = QApplication.clipboard()
# clipboard.setText("I've been clipped!")
# clipboard.text()
from limekit.framework.core.runner.app import App
from limekit.framework.core.engine.parts import EnginePart


class Clipboard(EnginePart):
    app = App.app.clipboard()
    name = "__clipboard"

    @staticmethod
    def setText(text):
        Clipboard.app.setText(text)

    @staticmethod
    def getText():
        return Clipboard.app.text()
