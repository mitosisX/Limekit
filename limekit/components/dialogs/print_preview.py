from PySide6.QtPrintSupport import QPrintPreviewDialog
from limekit.engine.parts import EnginePart


class PrintPreview(QPrintPreviewDialog, EnginePart):
    name = "__printPreview"

    def __init__(self, widget):
        super().__init__()

        self.paintRequested.connect(lambda p: widget(p))

    def show(self):
        self.exec()
