try:
    from PySide6.QtPrintSupport import QPrintPreviewDialog
    _HAS_PRINT_SUPPORT = True
except ImportError:
    _HAS_PRINT_SUPPORT = False
    QPrintPreviewDialog = object  # Fallback base class

from limekit.engine.parts import EnginePart


class PrintPreview(QPrintPreviewDialog, EnginePart):
    name = "__printPreview"

    def __init__(self, widget):
        if not _HAS_PRINT_SUPPORT:
            from limekit.core.error_handler import warn
            warn("PySide6.QtPrintSupport not available", "PrintPreview")
            return
        super().__init__()
        self.paintRequested.connect(lambda p: widget(p))

    def show(self):
        if not _HAS_PRINT_SUPPORT:
            return
        self.exec()
