from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QFont
from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtWidgets import QSizePolicy

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


class Label(QLabel, EnginePart):
    def __init__(self, text="Label"):
        super().__init__()

        self.pixmap = None

        self.setText(text)

    def onClick(self, func):
        self.clicked.connect(lambda: func(self))

    def setTextAlign(self, alignment):
        align = alignment.lower()

        if align == "left":
            self.setAlignment(Qt.AlignmentFlag.AlignLeft)

        elif align == "right":
            self.setAlignment(Qt.AlignmentFlag.AlignRight)

        elif align == "bottom":
            self.setAlignment(Qt.AlignmentFlag.AlignBottom)

        elif align == "top":
            self.setAlignment(Qt.AlignmentFlag.AlignTop)

        elif align == "center":
            self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def setImage(self, path):
        self.pixmap = QPixmap(path)

        # self.setScaledContents(True)
        self.setPixmap(self.pixmap)

    def resizeImage(self, width, height):
        self.pixmap.scaled(
            width, height, mode=Qt.TransformationMode.SmoothTransformation
        )

        self.setPixmap(self.pixmap)

    def getText(self):
        return self.text()

    def setFontFile(self, font):
        pass

    def setFont(self, font, size=0):
        if isinstance(font, QFont):
            super().setFont(font)
        else:
            super().setFont(QFont(font, size))

    def f(self, f):
        super().setFont(f)

    def setWordWrap(self, enable):
        super().setWordWrap(enable)

    def setCompanion(self, companion):
        self.setBuddy(companion)

    def setResizeRule(self, horizontal: str, vertical: str):
        policies = {
            "fixed": QSizePolicy.Policy.Fixed,  # ignores all size changing
            "expanding": QSizePolicy.Policy.Expanding,  # makes sure to expand to all available spaces
            "ignore": QSizePolicy.Policy.Ignored,  # does nothing
        }

        horizontal = horizontal.lower()
        vertical = vertical.lower()

        if (horizontal in policies) and (vertical in policies):
            size_policy = QSizePolicy(policies.get(horizontal), policies.get(vertical))
            self.setSizePolicy(size_policy)
