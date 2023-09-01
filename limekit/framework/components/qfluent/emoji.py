from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtWidgets import QVBoxLayout
from qfluentwidgets import (
    CaptionLabel,
    FluentIcon,
    CardWidget,
    RoundMenu,
    Action,
    ImageLabel,
)
from PySide6.QtCore import Qt, QPoint


class EmojiCard(EnginePart, CardWidget):
    def __init__(self, iconPath: str, label="Emoji", parent=None):
        super().__init__(parent)
        self.iconWidget = ImageLabel(iconPath, self)
        self.label = CaptionLabel(label, self)

        self.iconWidget.scaledToHeight(68)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignCenter)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.label, 0, Qt.AlignHCenter | Qt.AlignBottom)

        self.setFixedSize(168, 176)

    def onMoreButtonClicked(self):
        menu = RoundMenu(parent=self)
        menu.addAction(Action(FluentIcon.SHARE, "Share", self))
        menu.addAction(Action(FluentIcon.CHAT, "Chat", self))
        menu.addAction(Action(FluentIcon.PIN, "PIN", self))

        x = (self.moreButton.width() - menu.width()) // 2 + 10
        pos = self.moreButton.mapToGlobal(QPoint(x, self.moreButton.height()))
        menu.exec(pos)
