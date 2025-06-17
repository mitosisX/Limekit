import lupa

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QPixmap, QFont
from limekit.engine.parts import EnginePart
from limekit.components.base.widget_base import BaseWidget

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


class Label(BaseWidget, QLabel, EnginePart):
    onClickFunc = None

    # @lupa.unpacks_lua_table
    def __init__(self, text="Label"):
        super().__init__()

        self.pixmap = None
        self.image_path = ""

        self.setText(text)
        # self.clicked.connect(self.__handleOnClick)

    def mousePressEvent(self, ev: QMouseEvent):
        if self.onClickFunc:
            self.onClickFunc(self)
        return super().mousePressEvent(ev)

    def setOnClick(self, onClickFunc):
        self.onClickFunc = onClickFunc

    def setText(self, text):
        super().setText(str(text))

    def setBackgroundColor(self, color):
        super().setStyleSheet(f"background-color: {color};")

    def setTextColor(self, color):
        super().setStyleSheet(f"color: {color};")

    def setWhatsThis(self, desc):
        super().setWhatsThis(desc)

    # Can also be used to align an image
    def setTextAlignment(self, *alignments):
        alignment_flags = Qt.AlignmentFlag(0)  # Start with no flags

        for align in alignments:
            align = align.lower()

            if align == "left":
                alignment_flags |= Qt.AlignmentFlag.AlignLeft
            elif align == "right":
                alignment_flags |= Qt.AlignmentFlag.AlignRight
            elif align == "bottom":
                alignment_flags |= Qt.AlignmentFlag.AlignBottom
            elif align == "top":
                alignment_flags |= Qt.AlignmentFlag.AlignTop
            elif align == "center":
                alignment_flags |= Qt.AlignmentFlag.AlignCenter
            elif align == "hcenter":
                alignment_flags |= Qt.AlignmentFlag.AlignHCenter
            elif align == "vcenter":
                alignment_flags |= Qt.AlignmentFlag.AlignVCenter

        self.setAlignment(alignment_flags)

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
        self.image_path = path
        self.pixmap = QPixmap(self.image_path)

        # self.setScaledContents(True)
        self.setPixmap(self.pixmap)

    def getImagePath(self):
        return self.image_path

    def setImageSize(self, width, height):
        scaled = self.pixmap.scaled(
            width, height, mode=Qt.TransformationMode.SmoothTransformation
        )

        self.setPixmap(scaled)

    def resizeImage(self, width, height):
        scaled = self.pixmap.scaled(
            width, height, mode=Qt.TransformationMode.SmoothTransformation
        )

        self.setPixmap(scaled)

    def getText(self):
        return self.text()

    def setFontFile(self, font):
        pass

    def setFont(self, font, size=0):
        if isinstance(font, QFont):
            super().setFont(font)
        else:
            super().setFont(QFont(font, size))

    def setTextSize(self, size):
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)

    def setBold(self, set_bold: bool):
        font = self.font()
        font.setBold(set_bold)
        self.setFont(font)

    # def setTextSize(self, size):
    #     font = QFont()
    #     font.setPointSize(size)
    #     super().setFont(font)

    # def setBold(self, set_bold: bool):
    #     font = QFont()
    #     font.setBold(set_bold)
    #     super().setFont(font)

    def setWordWrap(self, enable: bool):
        super().setWordWrap(enable)

    def setCompanion(self, companion):
        self.setBuddy(companion)

    # def setResizeRule(self, horizontal: str, vertical: str):
    #     policies = {
    #         "fixed": QSizePolicy.Policy.Fixed,  # ignores all size changing
    #         "expanding": QSizePolicy.Policy.Expanding,  # makes sure to expand to all available spaces
    #         "ignore": QSizePolicy.Policy.Ignored,  # does nothing
    #     }

    #     horizontal = horizontal.lower()
    #     vertical = vertical.lower()

    #     if (horizontal in policies) and (vertical in policies):
    #         size_policy = QSizePolicy(policies.get(horizontal), policies.get(vertical))
    #         self.setSizePolicy(size_policy)
