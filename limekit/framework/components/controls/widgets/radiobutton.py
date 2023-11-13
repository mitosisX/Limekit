from PySide6.QtWidgets import QRadioButton
from limekit.framework.core.engine.parts import EnginePart


class RadioButton(QRadioButton, EnginePart):
    onClickFunc = None

    def __init__(self, text="RadioButton"):
        super().__init__(text, parent=None)

        self.clicked.connect(self.__handleOnClick)

        self.setText(text)

    def setOnClick(self, onClickFunc):
        self.onClickFunc = onClickFunc

    def __handleOnClick(self):
        if self.onClickFunc:
            self.onClickFunc(self)

    def getText(self):
        return self.text()
