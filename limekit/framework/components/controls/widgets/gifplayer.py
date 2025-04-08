from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy, QVBoxLayout
from PySide6.QtGui import QMovie
from PySide6.QtCore import QByteArray, Qt, QSize
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.components.base.base_widget import BaseWidget



class GifPlayer(QLabel, BaseWidget, EnginePart):
    def __init__(self, filename):
        super().__init__()
        BaseWidget.__init__(self, widget=self)

        # Load the file into a QMovie
        self.movie = QMovie(filename)

        # size = self.movie.scaledSize()
        # self.setGeometry(200, 200, size.width(), size.height())
        # self.setSize(20, 20)

        self.movie_screen = QLabel()

        # Make label fit the gif
        # self.movie_screen.setSizePolicy(
        #     QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        # )
        # self.movie_screen.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create the layout
        # main_layout = QVBoxLayout()
        # main_layout.addWidget(self.movie_screen)

        # self.setLayout(main_layout)

        # Add the QMovie object to the label
        self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
        # self.movie.setSpeed(100)
        self.setMovie(self.movie)
        self.movie.start()

    def setSize(self, width, height):
        self.movie.setScaledSize(QSize(width, height))

    def setSpeed(self, speed):
        self.movie.speed(speed)

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
