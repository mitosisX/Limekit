# coding:utf-8

from PySide6.QtCore import Qt, QSize, QRectF, QEvent
from PySide6.QtGui import QPixmap, QPainter, QColor, QIcon
from PySide6.QtWidgets import QWidget, QLabel, QGraphicsDropShadowEffect
from limekit.framework.core.engine.parts import EnginePart


class SplashScreen(QWidget, EnginePart):
    def __init__(self, icon, parent=None, enableShadow=True):
        super().__init__(parent=parent)
        self._icon = icon
        self._iconSize = QSize(96, 96)

        self.iconWidget = QLabel(self)

        pixmap = QPixmap(icon)

        # self.setScaledContents(True)
        self.iconWidget.setPixmap(
            pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio)
        )
        self.center()

        self.shadowEffect = QGraphicsDropShadowEffect(self)

        # self.iconWidget.setFixedSize(self._iconSize)
        self.shadowEffect.setColor(QColor(0, 0, 0, 50))
        self.shadowEffect.setBlurRadius(15)
        self.shadowEffect.setOffset(0, 4)

        if enableShadow:
            self.iconWidget.setGraphicsEffect(self.shadowEffect)

        if parent:
            parent.installEventFilter(self)

    def setIcon(self, icon):
        self._icon = icon
        self.update()

    def setIconSize(self, size: QSize):
        self._iconSize = size
        # self.iconWidget.setFixedSize(size)
        self.update()

    def iconSize(self):
        return self._iconSize

    def eventFilter(self, obj, e: QEvent):
        if obj is self.parent():
            if e.type() == QEvent.Resize:
                self.resize(e.size())
            elif e.type() == QEvent.ChildAdded:
                self.raise_()

        return super().eventFilter(obj, e)

    def resizeEvent(self, e):
        self.center()

    def center(self):
        iw, ih = self.iconSize().width(), self.iconSize().height()
        self.iconWidget.move(self.width() // 2 - iw // 2, self.height() // 2 - ih // 2)

    def finish(self):
        """close splash screen"""
        self.close()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)

        # draw background
        c = 255
        painter.setBrush(QColor(c, c, c))
        painter.drawRect(self.rect())
