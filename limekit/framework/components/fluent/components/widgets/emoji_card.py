from PySide6.QtCore import Qt
from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtWidgets import QVBoxLayout
from qfluentwidgets import (
    CaptionLabel,
    ElevatedCardWidget,
    ImageLabel,
)


class FEmojiCard(ElevatedCardWidget, EnginePart):
    def __init__(self, iconPath, label):
        super().__init__(parent=None)
        self.iconWidget = ImageLabel(iconPath, self)
        self.label = CaptionLabel(label, self)

        self.iconWidget.scaledToHeight(68)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(
            self.label, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom
        )

        self.setFixedSize(168, 176)

    def onClick(self, func):
        self.clicked.connect(lambda: func(self))
