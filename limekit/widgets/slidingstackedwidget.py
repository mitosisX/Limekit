"""A `QStackedWidget` that animates between pages instead of cutting.

Ports the public surface of 1.x's `SlidingStackedWidget`; the sliding
animation internals (`slideInWgt`/`_initAnimation`/etc.) are kept as-is,
they are what make this widget different from `Tab`/`StackedLayout`.

1.x defect not reproduced: `setAnimation` looked up the easing curve name
with `getattr(QEasingCurve.Type, animation)` and silently swallowed
`AttributeError` on a bad name -- `slider:setAnimation("bogus")` would
just do nothing, with no error anywhere. That now raises `BridgeError`.
The unused `pyqtProperty(int, ...)` declarations for speed/orientation/
easing (1.x) are dropped: nothing read them, `setSpeed`/`setOrientation`/
`setEasing` already are the real setters.
"""

from PySide6.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    Qt,
    QTimer,
)
from PySide6.QtWidgets import QStackedWidget, QWidget

from limekit.kernel.bridge.convert import to_lua
from limekit.kernel.coerce import ORIENTATIONS, Enum, LuaIndex
from limekit.kernel.errors import BridgeError
from limekit.widgets.base import LimeWidget, _to_int

_orientation = Enum(ORIENTATIONS, "orientation")


class SlidingStackedWidget(LimeWidget, QStackedWidget):
    __lime__ = "ui.SlidingStackedWidget"

    LEFT2RIGHT, RIGHT2LEFT, TOP2BOTTOM, BOTTOM2TOP, AUTOMATIC = range(5)

    def __init__(self):
        super().__init__()
        self._pnow = QPoint(0, 0)
        self._speed = 500
        self._now = 0
        self._current = 0
        self._next = 0
        self._active = 0
        self._orientation = Qt.Orientation.Horizontal
        self._easing = QEasingCurve.Type.Linear
        self._initAnimation()

    def addChild(self, child):
        self.addWidget(child)
        return self

    def addLayout(self, layout):
        widget = QWidget()
        widget.setLayout(layout)
        self.addWidget(widget)
        return self

    def getCount(self):
        return self.count()

    def slideNext(self):
        now = self.currentIndex()
        if now < self.count() - 1:
            self._current = now + 1
            self.slideInIdx(now + 1)
        return self

    def slidePrev(self):
        now = self.currentIndex()
        if now > 0:
            self._current = now - 1
            self.slideInIdx(now - 1)
        return self

    def setSpeed(self, speed=500):
        self._speed = _to_int(speed, "speed")
        return self

    def getAnimations(self):
        curve_types = sorted(
            n for n, c in QEasingCurve.Type.__dict__.items()
            if "_" not in n and n != "Custom"
        )
        return to_lua(curve_types)

    def setAnimation(self, animation):
        try:
            self._easing = getattr(QEasingCurve.Type, str(animation))
        except AttributeError:
            raise BridgeError(f"unknown easing curve {animation!r}") from None
        return self

    def setOrientation(self, orientation):
        self._orientation = _orientation(orientation)
        return self

    def setEasing(self, easing):
        return self.setAnimation(easing)

    def slideInIdx(self, idx, direction=None):
        if direction is None:
            direction = self.AUTOMATIC
        if idx > self.count() - 1:
            direction = (
                self.TOP2BOTTOM if self._orientation == Qt.Orientation.Vertical
                else self.RIGHT2LEFT
            )
            idx = idx % self.count()
        elif idx < 0:
            direction = (
                self.BOTTOM2TOP if self._orientation == Qt.Orientation.Vertical
                else self.LEFT2RIGHT
            )
            idx = (idx + self.count()) % self.count()
        self.slideInWgt(self.widget(idx), direction)
        return self

    def slideInWgt(self, widget, direction):
        if self._active:
            return
        self._active = 1
        _now = self.currentIndex()
        _next = self.indexOf(widget)
        if _now == _next:
            self._active = 0
            return

        w_now = self.widget(_now)
        w_next = self.widget(_next)

        if _now < _next:
            directionhint = (
                self.TOP2BOTTOM if self._orientation == Qt.Orientation.Vertical
                else self.RIGHT2LEFT
            )
        else:
            directionhint = (
                self.BOTTOM2TOP if self._orientation == Qt.Orientation.Vertical
                else self.LEFT2RIGHT
            )
        if direction == self.AUTOMATIC:
            direction = directionhint

        offsetX = self.frameRect().width()
        offsetY = self.frameRect().height()
        w_next.setGeometry(0, 0, offsetX, offsetY)

        if direction == self.BOTTOM2TOP:
            offsetX = 0
            offsetY = -offsetY
        elif direction == self.TOP2BOTTOM:
            offsetX = 0
        elif direction == self.RIGHT2LEFT:
            offsetX = -offsetX
            offsetY = 0
        elif direction == self.LEFT2RIGHT:
            offsetY = 0

        pnext = w_next.pos()
        pnow = w_now.pos()
        self._pnow = pnow

        w_next.move(pnext.x() - offsetX, pnext.y() - offsetY)
        w_next.show()
        w_next.raise_()

        self._animnow.setTargetObject(w_now)
        self._animnow.setDuration(self._speed)
        self._animnow.setEasingCurve(self._easing)
        self._animnow.setStartValue(QPoint(pnow.x(), pnow.y()))
        self._animnow.setEndValue(QPoint(offsetX + pnow.x(), offsetY + pnow.y()))

        self._animnext.setTargetObject(w_next)
        self._animnext.setDuration(self._speed)
        self._animnext.setEasingCurve(self._easing)
        self._animnext.setStartValue(QPoint(-offsetX + pnext.x(), offsetY + pnext.y()))
        self._animnext.setEndValue(QPoint(pnext.x(), pnext.y()))

        self._next = _next
        self._now = _now
        self._active = 1
        self._animgroup.start()

    def _initAnimation(self):
        self._animnow = QPropertyAnimation(
            self, propertyName=b"pos", duration=self._speed, easingCurve=self._easing
        )
        self._animnext = QPropertyAnimation(
            self, propertyName=b"pos", duration=self._speed, easingCurve=self._easing
        )
        self._animgroup = QParallelAnimationGroup(self, finished=self._animationDoneSlot)
        self._animgroup.addAnimation(self._animnow)
        self._animgroup.addAnimation(self._animnext)

    def setCurrentIndex(self, index):
        self.slideInIdx(LuaIndex(index))
        return self

    def getCurrentIndex(self):
        if self._active:
            return self._next + 1
        return self.currentIndex() + 1

    def setCurrentWidget(self, widget):
        super().setCurrentWidget(widget)
        self.setCurrentIndex(self.indexOf(widget) + 1)
        return self

    def _animationDoneSlot(self):
        QStackedWidget.setCurrentIndex(self, self._next)
        w = self.widget(self._now)
        w.hide()
        w.move(self._pnow)
        self._active = 0

    def autoStop(self):
        if hasattr(self, "_autoTimer"):
            self._autoTimer.stop()
        return self

    def autoStart(self, msec=3000):
        if not hasattr(self, "_autoTimer"):
            self._autoTimer = QTimer(self, timeout=self._autoAdvance)
        self._autoTimer.stop()
        self._autoTimer.start(_to_int(msec, "msec"))
        return self

    def _autoAdvance(self):
        if self._current == self.count():
            self._current = 0
        self._current += 1
        self.setCurrentIndex(self._current)
