from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QWidget
from limekit.framework.core.engine.parts import EnginePart


class Scrollable(QScrollArea, EnginePart):
    onValueChangeFunc = None

    def __init__(self):
        super().__init__(parent=None)
        self.parent_widget = QWidget()
        self.setWidget(self.parent_widget)

        self.setHorizontalScrollProperty("required")
        self.setVerticalScrollProperty("required")
        self.setResizable(True)

    def setLayout(self, layout):
        self.parent_widget.setLayout(layout)

    def setResizable(self, resizable):
        self.setWidgetResizable(resizable)

    def __decideScrollProperty(self, prop):
        policy = Qt.ScrollBarPolicy.ScrollBarAsNeeded

        match (prop.lower()):
            case ("required"):
                policy = Qt.ScrollBarPolicy.ScrollBarAsNeeded
            case ("hidden"):
                policy = Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            case ("always"):
                policy = Qt.ScrollBarPolicy.ScrollBarAlwaysOn

        return policy

    def setHorizontalScrollProperty(self, prop):
        self.setHorizontalScrollBarPolicy(self.__decideScrollProperty(prop))

    def setVerticalScrollProperty(self, prop):
        self.setVerticalScrollBarPolicy(self.__decideScrollProperty(prop))
