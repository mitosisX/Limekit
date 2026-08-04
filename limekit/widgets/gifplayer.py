"""Animated GIF playback (QMovie inside a QLabel)."""

from PySide6.QtCore import QSize
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import QLabel

from limekit.kernel.coerce import LuaIndex
from limekit.widgets.base import LimeWidget, _to_int


class GifPlayer(LimeWidget, QLabel):
    __lime__ = "ui.GifPlayer"

    def __init__(self, filename):
        super().__init__()
        self.movie = QMovie(str(filename))
        self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
        self.setMovie(self.movie)
        # Don't autostart immediately -- let setSize be called first if the
        # caller wants a scaled size, same as 1.x.
        self._autostart_pending = True

    def showEvent(self, event):
        super().showEvent(event)
        if self._autostart_pending:
            self._autostart_pending = False
            self.movie.start()

    def setSize(self, width, height):
        """Overrides LimeWidget.setSize: this scales the *movie*, not the
        widget geometry -- that is what the 1.x semantics were."""
        was_running = self.movie.state() == QMovie.MovieState.Running
        if was_running:
            self.movie.stop()

        self.movie.setScaledSize(QSize(_to_int(width, "width"), _to_int(height, "height")))

        if was_running or self._autostart_pending:
            self._autostart_pending = False
            self.movie.start()
        return self

    def getSpeed(self):
        return self.movie.speed()

    def setSpeed(self, speed):
        self.movie.setSpeed(_to_int(speed, "speed"))
        return self

    def pause(self):
        self.movie.setPaused(True)
        return self

    def start(self):
        self.movie.start()
        return self

    def stop(self):
        self.movie.stop()
        return self

    def nextFrame(self):
        self.movie.jumpToNextFrame()
        return self

    def getFramesCount(self):
        return self.movie.frameCount()

    def getCurrentFrame(self):
        """1-indexed, like every other Limekit collection accessor."""
        return self.movie.currentFrameNumber() + 1

    def jumpToFrame(self, frame):
        self.movie.jumpToFrame(LuaIndex(frame))
        return self

    def getState(self):
        state = self.movie.state()
        states = self.movie.MovieState
        if state == states.NotRunning:
            return "notrunning"
        if state == states.Paused:
            return "paused"
        return "running"
