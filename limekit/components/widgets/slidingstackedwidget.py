from PySide6.QtCore import (
    Qt,
    Property as pyqtProperty,
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    QParallelAnimationGroup,
    QTimer,
)
from PySide6.QtWidgets import QWidget, QStackedWidget
from limekit.engine.parts import EnginePart
from limekit.utils.converters import Converter


class SlidingStackedWidget(QStackedWidget, EnginePart):
    LEFT2RIGHT, RIGHT2LEFT, TOP2BOTTOM, BOTTOM2TOP, AUTOMATIC = range(5)

    def __init__(self):
        super().__init__(parent=None)
        self._pnow = QPoint(0, 0)
        self._speed = 500
        self._now = 0
        self._current = 0
        self._next = 0
        self._active = 0
        self._orientation = Qt.Horizontal
        self._easing = QEasingCurve.Linear
        self._initAnimation()

    def addLayout(self, layout):
        widget = QWidget()
        widget.setLayout(layout)
        self.addChild(widget)

    def getCount(self):
        return self.count()

    def addChild(self, child):
        self.addWidget(child)

    def slideNext(self):
        now = self.currentIndex()
        if now < self.count() - 1:
            self._current = now + 1  # Update immediately
            self.slideInIdx(now + 1)

    def slidePrev(self):
        now = self.currentIndex()
        if now > 0:
            self._current = now - 1  # Update immediately
            self.slideInIdx(now - 1)

    def setSpeed(self, speed=500):
        self._speed = speed

    @pyqtProperty(int, fset=setSpeed)
    def speed(self):
        return self._speed

    def getAnimations(self):
        curve_types = [
            n
            for n, c in QEasingCurve.Type.__dict__.items()
            if "_" not in n and n != "Custom"
        ]

        curve_types.sort()

        return Converter.table_from(curve_types)

    def setAnimation(self, animation):
        try:
            self.setEasing(getattr(QEasingCurve.Type, animation))
        except AttributeError:
            pass

    def setOrientation(self, orientation):
        if orientation == "horizontal":
            self._orientation = Qt.Orientation.Horizontal

        elif orientation == "vertical":
            self._orientation = Qt.Orientation.Vertical

    def setOrientation_(self, orientation=Qt.Horizontal):
        self._orientation = orientation

    @pyqtProperty(int, fset=setOrientation_)
    def orientation(self):
        return self._orientation

    def setEasing(self, easing=QEasingCurve.OutBack):
        self._easing = easing

    @pyqtProperty(int, fset=setEasing)
    def easing(self):
        return self._easing

    # def slideInNext(self):
    #     now = self.currentIndex()
    #     if now < self.count() - 1:
    #         self.slideInIdx(now + 1)
    #         self._current = now + 1

    # def slideInPrev(self):
    #     now = self.currentIndex()
    #     if now > 0:
    #         self.slideInIdx(now - 1)
    #         self._current = now - 1

    def slideInIdx(self, idx, direction=4):
        if idx > self.count() - 1:
            direction = (
                self.TOP2BOTTOM if self._orientation == Qt.Vertical else self.RIGHT2LEFT
            )
            idx = idx % self.count()
        elif idx < 0:
            direction = (
                self.BOTTOM2TOP if self._orientation == Qt.Vertical else self.LEFT2RIGHT
            )
            idx = (idx + self.count()) % self.count()
        self.slideInWgt(self.widget(idx), direction)

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
                self.TOP2BOTTOM if self._orientation == Qt.Vertical else self.RIGHT2LEFT
            )
        else:
            directionhint = (
                self.BOTTOM2TOP if self._orientation == Qt.Vertical else self.LEFT2RIGHT
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

        self._animgroup = QParallelAnimationGroup(self, finished=self.animationDoneSlot)
        self._animgroup.addAnimation(self._animnow)
        self._animgroup.addAnimation(self._animnext)

    def setCurrentIndex(self, index):
        self.slideInIdx(index - 1)  # Why subtract 1 here?

    def getCurrentIndex(self):
        if self._active:
            return self._next + 1  # Return the target index during animation
        return self.currentIndex() + 1

    def setCurrentWidget(self, widget):
        super(SlidingStackedWidget, self).setCurrentWidget(widget)
        self.setCurrentIndex(self.indexOf(widget))

    def animationDoneSlot(self):
        QStackedWidget.setCurrentIndex(self, self._next)
        w = self.widget(self._now)
        w.hide()
        w.move(self._pnow)
        self._active = 0

    def autoStop(self):
        if hasattr(self, "_autoTimer"):
            self._autoTimer.stop()

    def autoStart(self, msec=3000):
        if not hasattr(self, "_autoTimer"):
            self._autoTimer = QTimer(self, timeout=self._autoStart)
        self._autoTimer.stop()
        self._autoTimer.start(msec)

    def _autoStart(self):
        if self._current == self.count():
            self._current = 0
        self._current += 1
        self.setCurrentIndex(self._current)
