"""A modal dialog window.

Like Window, `showEvent`/`closeEvent`/`resizeEvent` are Qt virtual-method
overrides rather than signals, so they cannot use the declarative `Event`
spec; they are hand-written but still cross `guard()`.

1.x's `show()` called `self.exec()` -- Qt's *blocking* modal event loop --
so `modal:show()` silently meant something completely different from every
other widget's `show()`, and would hang a headless test dead. That method
is not reproduced; `LimeWidget.show()` (non-blocking) is inherited as-is,
and blocking modal behaviour is available explicitly via `open()`.
"""

from PySide6.QtWidgets import QDialog

from limekit.kernel.bridge.guard import guard
from limekit.kernel.coerce import Icon
from limekit.kernel.spec import Prop
from limekit.widgets.base import LimeWidget


class Modal(LimeWidget, QDialog):
    __lime__ = "ui.Modal"

    title = Prop(str, qt=("windowTitle", "setWindowTitle"), coerce=str)
    icon = Prop(object, qt=("windowIcon", "setWindowIcon"), coerce=Icon)
    modal = Prop(bool, qt=("isModal", "setModal"))
    layout = Prop(object, qt=("layout", "setLayout"))

    def __init__(self, title="Modal", parent=None):
        super().__init__(parent)
        self._onShown = None
        self._onClose = None
        self._onResize = None
        self.setTitle(str(title))
        self.setModal(True)

    def open(self):
        """Blocking modal loop -- what 1.x's `show()` actually did."""
        return self.exec()

    def dismiss(self):
        self.close()
        return self

    # -- events ------------------------------------------------------------

    def setOnShown(self, handler):
        self._onShown = guard(handler, widget="Modal", event="onShown")
        return self

    def setOnClose(self, handler):
        self._onClose = guard(handler, widget="Modal", event="onClose")
        return self

    def setOnResize(self, handler):
        self._onResize = guard(handler, widget="Modal", event="onResize")
        return self

    def showEvent(self, event):
        super().showEvent(event)
        if self._onShown:
            self._onShown(self)

    def closeEvent(self, event):
        if self._onClose:
            self._onClose(self, event)
        if event.isAccepted():
            super().closeEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._onResize:
            width, height = event.size().width(), event.size().height()
            self._onResize(self, width, height)
