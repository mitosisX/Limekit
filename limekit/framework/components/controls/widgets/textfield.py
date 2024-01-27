from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QTextListFormat, QFont, QTextTableFormat
from limekit.framework.core.engine.parts import EnginePart


class TextField(QTextEdit, EnginePart):
    onTextChangedFunc = None
    onTextSelectionChangedFunc = None
    onCursorPositionChangedFunc = None

    def __init__(self, text=""):
        super().__init__(text)

        self.textChanged.connect(self.__handleTextChange)
        self.cursorPositionChanged.connect(self.__handleCursorChange)
        # self.selectionChanged.connect(self.__handleTextSelection)

    # Events ---------------------------------
    def setOnCursorPositionChange(self, onCursorPositionChangedFunc):
        self.onCursorPositionChangedFunc = onCursorPositionChangedFunc

    def setOnTextChange(self, onTextChangedFunc):
        self.onTextChangedFunc = onTextChangedFunc

    def __handleCursorChange(self):
        if self.onCursorPositionChangedFunc:
            self.onCursorPositionChangedFunc(self)

    def __handleTextChange(self):
        if self.onTextChangedFunc:
            self.onTextChangedFunc(self, self.getText())

    # def setOnSelection(self, onTextSelectionChangedFunc):
    #     self.onTextSelectionChangedFunc = onTextSelectionChangedFunc

    def __handleTextSelection(self):
        if self.onTextSelectionChangedFunc:
            self.onTextSelectionChangedFunc(self, self.selectedText())

    # --------------------------------- Events

    def setSize(self, width, height):
        self.resize(width, height)

    def setMinHeight(self, height):
        self.setMinimumHeight(height)

    def setMaxHeight(self, height):
        self.setMaximumHeight(height)

    def setMinWidth(self, width):
        self.setMinimumWidth(width)

    def setMaxWidth(self, width):
        self.setMaximumWidth(width)

    def setReadOnly(self, readonly):
        super().setReadOnly(readonly)

    def setHint(self, hint):
        self.setPlaceholderText(hint)

    def selectAll(self):
        super().selectAll()

    def cut(self):
        super().cut()

    def copy(self):
        super().copy()

    def paste(self):
        super().paste()

    def undo(self):
        super().undo()

    def redo(self):
        super().redo()

    def appendText(self, text):
        self.append(text)

    def setText(self, text):
        super().setText(text)

    def setPlainText(self, text):
        super().setPlainText(text)

    def getText(self):
        return self.toPlainText()

    # All new
    def getHtmlText(self):
        return self.toHtml()

    def print(self):
        self.print_()

    def setCursorTextFormat(self, format):
        cursor = self.__getCursor()
        cursor.insertList(self.__decideTextFormat(format))

    def __decideTextFormat(self, format):
        formats = {
            "listupperroman": QTextListFormat.Style.ListUpperRoman,
            "listlowerroman": QTextListFormat.Style.ListLowerRoman,
            "listupperalpha": QTextListFormat.Style.ListUpperAlpha,
            "listloweralpha": QTextListFormat.Style.ListLowerAlpha,
            "listdecimal": QTextListFormat.Style.ListDecimal,
            "listsquare": QTextListFormat.Style.ListSquare,
            "listcircle": QTextListFormat.Style.ListCircle,
            "listdisc": QTextListFormat.Style.ListDisc,
            "undefined": QTextListFormat.Style.ListStyleUndefined,
        }

        return formats.get(format) if format in formats else format.get("undefined")

    def addCursorTable(self, rows, columns, padding, spacing):
        fmt = QTextTableFormat()

        fmt.setCellPadding(padding)

        fmt.setCellSpacing(spacing)

        # Inser the new table
        self.__getCursor().insertTable(rows, columns, fmt)

    # How much spacing on Tab button press
    def setTabSpacing(self, spacing):
        self.setTabStopDistance(spacing)

    def getBlockNumber(self):
        return self.__getCursor().blockNumber()

    def getColumnNumber(self):
        return self.__getCursor().columnNumber()

    def __getCursor(self):
        return self.textCursor()

    def setTextSize(self, size):
        self.setFontPointSize(int(size))

    def setFont(self, font_):
        font = QFont()
        font.fromString(font_)
        self.setCurrentFont(font)

    def setTextColor(self, color):
        super().setTextColor(color)

    def setTextBgColor(self, color):
        super().setTextBackgroundColor(color)

    def isTextItalic(self):
        return self.fontItalic()

    def setTextItalic(self, italic):
        self.setFontItalic(italic)

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

        elif align == "hcenter":
            self.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        elif align == "vcenter":
            self.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        elif align == "justify":
            self.setAlignment(Qt.AlignmentFlag.AlignJustify)
