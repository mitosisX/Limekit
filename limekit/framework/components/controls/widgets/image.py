import lupa

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QMouseEvent, QPixmap, QFont
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


class Image(QLabel, EnginePart):
    onClickFunc = None

    @lupa.unpacks_lua_table
    def __init__(self, kwargs):
        super().__init__()

        self.pixmap = None
        self.setImage(kwargs["path"] or "")

        if "size" in kwargs:
            width, height = kwargs["size"]
            self.resizeImage(width, height)

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
