from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from limekit.framework.core.engine.parts import EnginePart

#   Alignments
# 1. Qt.AlignLeft
# 2. Qt.AlignRight
# 3. Qt.AlignBottom
# 4. Qt.AlignTop
# 5. Qt.AlignCenter
# 6. Qt.AlignHCenter
# 7. Qt.AlignVCenter

"""
When using & as a keyboard accelerator, the method setBuddy() has to
used to activate the feature.

label.setBuddy(textEdit) allows the framework to use the & as an accelerator
and not to be treated as an ordinary character.

label.setWordWrap(bool) makes the label multiline
"""


class Label(EnginePart, QLabel):
    def __init__(self, text="Label"):
        super().__init__()

        self.setText(text)

    def onClick(self, func):
        self.clicked.connect(lambda: func(self))

    def setTextAlign(self, alignment):
        align = alignment.lower()

        if align == "left":
            self.setAlignment(Qt.AlignLeft)

        elif align == "right":
            self.setAlignment(Qt.AlignRight)

        elif align == "bottom":
            self.setAlignment(Qt.AlignBottom)

        elif align == "top":
            self.setAlignment(Qt.AlignTop)

        elif align == "center":
            self.setAlignment(Qt.AlignCenter)

    def setImage(self, path):
        pixmap = QPixmap(path)
        # self.setScaledContents(True)
        self.setPixmap(pixmap)

    def getText(self):
        return self.text()
