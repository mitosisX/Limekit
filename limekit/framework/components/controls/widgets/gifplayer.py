from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy, QVBoxLayout
from PySide6.QtGui import QMovie
from PySide6.QtCore import QByteArray, Qt
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.components.base.base_widget import BaseWidget


class GifPlayer(QWidget, BaseWidget, EnginePart):
    def __init__(self, filename):
        QWidget.__init__(self)
        BaseWidget.__init__(self, widget=self)

        # Load the file into a QMovie
        self.movie = QMovie(filename, QByteArray(), self)

        size = self.movie.scaledSize()
        # self.setGeometry(200, 200, size.width(), size.height())
        self.resize(50, 50)

        self.movie_screen = QLabel()
        # Make label fit the gif
        self.movie_screen.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.movie_screen.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create the layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.movie_screen)

        self.setLayout(main_layout)

        # Add the QMovie object to the label
        self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
        self.movie.setSpeed(100)
        self.movie_screen.setMovie(self.movie)
        self.movie.start()
