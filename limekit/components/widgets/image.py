from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QPixmap
from limekit.engine.parts import EnginePart
from PySide6.QtWidgets import QSizePolicy


class Image(QLabel, EnginePart):
    onClickFunc = None

    # @lupa.unpacks_lua_table
    def __init__(self, path):
        super().__init__()

        self.pixmap = None
        self.image_path = path
        self.setImage(self.image_path)

        # if "size" in kwargs:
        #     width, height = kwargs["size"].values()

        #     self.resizeImage(width, height)

    def mousePressEvent(self, ev: QMouseEvent):
        if self.onClickFunc:
            self.onClickFunc(self)
        return super().mousePressEvent(ev)

    def setOnClick(self, onClickFunc):
        self.onClickFunc = onClickFunc

    def setImageAlignment(self, alignment):
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

        elif align == "hcenter":
            self.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        elif align == "vcenter":
            self.setAlignment(Qt.AlignmentFlag.AlignVCenter)

    def setImage(self, path):
        self.pixmap = QPixmap(path)

        # self.setScaledContents(True)
        self.setPixmap(self.pixmap)

    def getImagePath(self):
        return self.image_path

    def resizeImage(self, width, height):
        scaled = self.pixmap.scaled(
            width, height, mode=Qt.TransformationMode.SmoothTransformation
        )

        self.setPixmap(scaled)

    def setImageSize(self, width, height):
        scaled = self.pixmap.scaled(
            width, height, mode=Qt.TransformationMode.SmoothTransformation
        )

        self.setPixmap(scaled)

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
