"""A modal dialog window.

Like Window, `showEvent`/`closeEvent`/`resizeEvent` are Qt virtual-method
overrides rather than signals, so they cannot use the declarative `Event`
spec; they are hand-written but still cross `guard()`.

1.x's `show()` called `self.exec()` -- Qt's *blocking* modal event loop --
so `modal:show()` silently meant something completely different from every
other widget's `show()`, and would hang a headless test dead. That method
is not reproduced; `LimeWidget.show()` (non-blocking) is inherited as-is,
and blocking modal behaviour is available explicitly via `open()`.

Frameless + fade make a Modal usable as a card -- a splash screen, an About
box: no title bar, the modal's own background as the surface, and an opacity
animation in and out.
"""

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtWidgets import QDialog

from limekit.kernel.bridge.guard import guard
from limekit.kernel.coerce import Icon
from limekit.kernel.spec import Prop, method
from limekit.widgets.base import LimeWidget, close_permitted


def _duration(value, default):
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return default


class Modal(LimeWidget, QDialog):
    __lime__ = "ui.Modal"

    title = Prop(str, qt=("windowTitle", "setWindowTitle"), coerce=str)
    icon = Prop(object, qt=("windowIcon", "setWindowIcon"), coerce=Icon)
    modal = Prop(bool, qt=("isModal", "setModal"))
    layout = Prop(object, qt=("layout", "setLayout"))
    opacity = Prop(float, qt=("windowOpacity", "setWindowOpacity"), coerce=float,
                   doc="the whole window's opacity, from 0.0 to 1.0")

    def __init__(self, title="Modal", parent=None):
        super().__init__(parent)
        self._onShown = None
        self._onClose = None
        self._onResize = None
        self._onMousePress = None
        self._fade = None
        self._fading_out = False
        self.setTitle(str(title))
        self.setModal(True)

    def open(self):
        """Blocking modal loop -- what 1.x's `show()` actually did."""
        return self.exec()

    def dismiss(self):
        self.close()
        return self

    # -- card ----------------------------------------------------------------

    @method({"on": "boolean"}, returns="self",
            doc="No title bar or border: the modal's own background is the "
                "whole surface, e.g. for a splash screen or an About card. "
                "Call before show().")
    def setFrameless(self, on=True):
        # Opaque on purpose. A transparent margin around a rounded child looks
        # like a card in a render, but Windows 11 draws its own 1px border
        # round the whole window, margin included -- two outlines, one card.
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, bool(on))
        return self

    @method(returns="boolean", doc="Whether setFrameless is on.")
    def isFrameless(self):
        return bool(self.windowFlags() & Qt.WindowType.FramelessWindowHint)

    @method({"duration": "integer"}, returns="self",
            doc="Shows the modal, fading it in over `duration` ms (default 450).")
    def fadeIn(self, duration=450):
        self._fading_out = False
        self.setWindowOpacity(0.0)
        self.show()
        self._animate(1.0, _duration(duration, 450), QEasingCurve.Type.OutCubic)
        return self

    @method({"duration": "integer"}, returns="self",
            doc="Fades the modal out over `duration` ms (default 250), then "
                "closes it. Calling it again while it fades does nothing.")
    def fadeOut(self, duration=250):
        if self._fading_out:
            return self
        self._fading_out = True
        # From wherever a fade-in got to, so an early exit never pops back to full.
        self._animate(0.0, _duration(duration, 250), QEasingCurve.Type.InCubic,
                      then=self._faded_out)
        return self

    def _faded_out(self):
        self.close()
        # Ready to be shown again at full opacity.
        self._fading_out = False
        self.setWindowOpacity(1.0)

    def _animate(self, end, duration, curve, then=None):
        if self._fade is not None:
            self._fade.stop()
        fade = QPropertyAnimation(self, b"windowOpacity", self)
        fade.setDuration(duration)
        fade.setStartValue(self.windowOpacity())
        fade.setEndValue(end)
        fade.setEasingCurve(curve)
        if then is not None:
            fade.finished.connect(then)
        self._fade = fade
        fade.start()

    # -- events ------------------------------------------------------------

    def setOnShown(self, handler):
        self._onShown = guard(handler, widget="Modal", event="onShown")
        return self

    @method({"handler": "fun(modal: ui.Modal, request: any): boolean?"}, returns="self",
            doc="Runs when the modal is asked to close. Return false to keep "
                "it open.")
    def setOnClose(self, handler):
        self._onClose = guard(handler, widget="Modal", event="onClose")
        return self

    def setOnResize(self, handler):
        self._onResize = guard(handler, widget="Modal", event="onResize")
        return self

    @method({"handler": "fun(modal: ui.Modal, x: integer, y: integer)"}, returns="self",
            doc="Runs when the modal is clicked, with where, in its own "
                "coordinates -- e.g. to dismiss a card on any click.")
    def setOnMousePress(self, handler):
        self._onMousePress = guard(handler, widget="Modal", event="onMousePress")
        return self

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self._onMousePress:
            pos = event.position()
            self._onMousePress(self, int(pos.x()), int(pos.y()))

    def showEvent(self, event):
        super().showEvent(event)
        if self._onShown:
            self._onShown(self)

    def closeEvent(self, event):
        if close_permitted(self._onClose, self, event):
            super().closeEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._onResize:
            width, height = event.size().width(), event.size().height()
            self._onResize(self, width, height)
