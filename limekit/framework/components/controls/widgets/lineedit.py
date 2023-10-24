from PySide6.QtWidgets import QLineEdit
from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtCore import Qt
import lupa


# setInputMask("AAAA.AAA.000.000;_"); - limits text to st then ints
class LineEdit(QLineEdit, EnginePart):
    onTextChangedFunc = None
    onReturnPressedFunc = None
    onTextSelectionChangedFunc = None

    def __init__(self, text=""):
        super().__init__(text)
        self.textChanged.connect(self.__handleTextChange)
        self.returnPressed.connect(self.__handleReturnPress)
        self.selectionChanged.connect(self.__handleTextSelection)

    # Events ---------------------------------
    def setOnTextChange(self, onTextChangedFunc):
        self.onTextChangedFunc = onTextChangedFunc

    def __handleTextChange(self):
        if self.onTextChangedFunc:
            self.onTextChangedFunc(self, self.getText())

    def setOnReturnPress(self, onReturnPressedFunc):
        self.onReturnPressedFunc = onReturnPressedFunc

    def __handleReturnPress(self):
        if self.onReturnPressedFunc:
            self.onReturnPressedFunc(self)

    def setOnSelection(self, onTextSelectionChangedFunc):
        self.onTextSelectionChangedFunc = onTextSelectionChangedFunc

    def __handleTextSelection(self):
        if self.onTextSelectionChangedFunc:
            self.onTextSelectionChangedFunc(self, self.selectedText())

    # --------------------------------- Events

    def setInputMode(self, input_mode):
        mode = input_mode.lower()

        if mode == "normal":
            self.setEchoMode(QLineEdit.Normal)

        elif mode == "password":
            self.setEchoMode(QLineEdit.Password)

    def setText(self, text):
        super().setText(text)

    def setHint(self, hint):
        self.setPlaceholderText(hint)

    def getText(self):
        return self.text()

    def getSelectedText(self):
        super().selectedText()

    def checkSelectedText(self):
        return self.hasSelectedText()

    def redo(self):
        super().redo()

    def undo(self):
        super().undo()

    @lupa.unpacks_lua_table
    def setTextMargins(self, left=0, top=0, right=0, bottom=0):
        super().setTextMargins(left, top, right, bottom)

    def setReadOnly(self, readonly):
        super().setReadOnly(readonly)

    def setMaxLength(self, max_length):
        super().setMaxLength(max_length)

    def selectAll(self):
        super().selectAll()

    def getEndSelection(self):
        return self.selectionEnd()

    def getSelectionLength(self):
        return self.selectionLength()

    def getStartSelection(self):
        return self.selectionStart()

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

    def setCursorMoveStyle(self, style):
        super().setCursorMoveStyle(Qt.CursorMoveStyle.VisualMoveStyle)
