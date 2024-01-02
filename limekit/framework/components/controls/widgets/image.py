from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QPixmap
from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtWidgets import QSizePolicy


class Image(QLabel, EnginePart):
    onClickFunc = None

    # @lupa.unpacks_lua_table
    def __init__(self, path):
        super().__init__()

        self.pixmap = None

        self.setImage(path)

        # if "size" in kwargs:
        #     width, height = kwargs["size"].values()

        #     self.resizeImage(width, height)

    def mousePressEvent(self, ev: QMouseEvent):
        if self.onClickFunc:
            self.onClickFunc(self)
        return super().mousePressEvent(ev)

    def setOnClick(self, onClickFunc):
        self.onClickFunc = onClickFunc

    def setCursor(self, cursor_type):
        cursors = {
            "wait": Qt.CursorShape.ArrowCursor,
            "uparrow": Qt.CursorShape.UpArrowCursor,
            "cross": Qt.CursorShape.CrossCursor,
            "ibeam": Qt.CursorShape.IBeamCursor,
            "sizever": Qt.CursorShape.SizeVerCursor,
            "sizehor": Qt.CursorShape.SizeHorCursor,
            "sizebdiag": Qt.CursorShape.SizeBDiagCursor,
            "sizefdiag": Qt.CursorShape.SizeFDiagCursor,
            "sizeall": Qt.CursorShape.SizeAllCursor,
            "blank": Qt.CursorShape.BlankCursor,
            "splitv": Qt.CursorShape.SplitVCursor,
            "splith": Qt.CursorShape.SplitHCursor,
            "pointinghand": Qt.CursorShape.PointingHandCursor,
            "forbidden": Qt.CursorShape.ForbiddenCursor,
            "whatsthis": Qt.CursorShape.WhatsThisCursor,
            "busy": Qt.CursorShape.BusyCursor,
            "openhand": Qt.CursorShape.OpenHandCursor,
            "closedhand": Qt.CursorShape.ClosedHandCursor,
            "dragcopy": Qt.CursorShape.DragCopyCursor,
            "dragmove": Qt.CursorShape.DragMoveCursor,
            "draglink": Qt.CursorShape.DragLinkCursor,
            "last": Qt.CursorShape.LastCursor,
            "bitmap": Qt.CursorShape.BitmapCursor,
            "openhand": Qt.CursorShape.CustomCursor,
        }

        super().setCursor(cursors.get(cursor_type) or cursors["ibeam"])

    def setImageAlign(self, alignment):
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

    def resizeImage(self, width, height):
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
