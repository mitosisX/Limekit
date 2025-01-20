from limekit.framework.core.engine.parts import EnginePart
from qfluentwidgets import CardWidget, IconWidget, TextWrap, isDarkTheme
from PySide6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt


class InfoCard(CardWidget, EnginePart):
    def __init__(self, icon, title, content, parent=None):
        super().__init__(parent=parent)

        self.iconWidget = IconWidget(icon, self)
        self.titleLabel = QLabel(title, self)
        self.contentLabel = QLabel(TextWrap.wrap(content, 45, False)[0], self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedSize(360, 90)
        self.iconWidget.setFixedSize(48, 48)

        self.hBoxLayout.setSpacing(28)
        self.hBoxLayout.setContentsMargins(20, 0, 0, 0)
        self.vBoxLayout.setSpacing(2)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)

        self.hBoxLayout.setAlignment(Qt.AlignVCenter)
        self.hBoxLayout.addWidget(self.iconWidget)
        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addWidget(self.contentLabel)
        self.vBoxLayout.addStretch(1)

        self.titleLabel.setObjectName("titleLabel")
        self.contentLabel.setObjectName("contentLabel")

        if isDarkTheme():
            self.setStyleSheet(
                """                
                #titleLabel {
                    color: white;
                    font: 14px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC';
                    font-weight: bold;
                }

                #contentLabel {
                    color: rgb(208, 208, 208);
                    font: 12px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC';
                }

                #viewTitleLabel {
                    color: white;
                    font: 20px "Segoe UI SemiBold", "Microsoft YaHei", 'PingFang SC';
                }
                """
            )
        else:
            self.setStyleSheet(
                """
                #titleLabel {
                    color: black;
                    font: 14px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC';
                    font-weight: bold;
                }

                #contentLabel {
                    color: rgb(118, 118, 118);
                    font: 12px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC';
                }

                #viewTitleLabel {
                    color: black;
                    font: 20px "Segoe UI SemiBold", "Microsoft YaHei", 'PingFang SC';
                }
                """
            )

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        # signalBus.switchToSampleCard.emit(self.routekey, self.index)
