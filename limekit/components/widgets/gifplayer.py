from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy, QVBoxLayout
from PySide6.QtGui import QMovie
from PySide6.QtCore import QByteArray, Qt, QSize
from limekit.engine.parts import EnginePart
from limekit.components.base.widget_base import BaseWidget


class GifPlayer(BaseWidget, QLabel, EnginePart):
    def __init__(self, filename):
        super().__init__()

        # Load the file into a QMovie
        self.movie = QMovie(filename)

        # Add the QMovie object to the label with caching enabled
        self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
        self.setMovie(self.movie)
        # Don't start automatically - let setSize be called first if needed
        self._autostart_pending = True

    def showEvent(self, event):
        """Start movie when widget becomes visible, if not already started."""
        super().showEvent(event)
        if self._autostart_pending:
            self._autostart_pending = False
            self.movie.start()

    def setSize(self, width, height):
        was_running = self.movie.state() == QMovie.MovieState.Running

        # Stop the movie before changing size to prevent flickering
        if was_running:
            self.movie.stop()

        self.movie.setScaledSize(QSize(width, height))

        # Restart if it was running, or start if autostart is pending
        if was_running or self._autostart_pending:
            self._autostart_pending = False
            self.movie.start()

    def setSpeed(self, speed):
        self.movie.setSpeed(speed)

    def pause(self):
        self.movie.setPaused(True)

    def start(self):
        self.movie.start()

    def getFramesCount(self):
        return self.movie.frameCount()

    def stop(self):
        self.movie.stop()

    def nextFrame(self):
        self.movie.jumpToNextFrame()

    def getCurrentFrame(self):
        return self.movie.currentFrameNumber()

    def justToFrame(self, frame):
        self.movie.jumpToFrame(frame)

    def getState(self):
        state = self.movie.state()
        movie_state = self.movie.MovieState

        if state == movie_state.NotRunning:
            return "notrunning"

        elif state == movie_state.Paused:
            return "paused"

        elif state == movie_state.Running:
            return "running"
