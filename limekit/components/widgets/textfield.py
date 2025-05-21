from PySide6.QtCore import Qt, QSizeF
from PySide6.QtWidgets import QTextEdit, QFrame
from PySide6.QtGui import (
    QTextListFormat,
    QFont,
    QTextTableFormat,
    QTextCharFormat,
    QKeyEvent,
)
from limekit.engine.parts import EnginePart
from limekit.components.base.base_widget import BaseWidget


class TextField(BaseWidget, QTextEdit, EnginePart):
    onTextChangedFunc = None
    onTextSelectionChangedFunc = None
    onCursorPositionChangedFunc = None
    onKeyPressChangeFunc = None
    onContentChangeFunc = None
    onModificationChangeFunc = None
    onVerticalScrollBarValueChangeFunc = None
    onHorizontalScrollBarValueChangeFunc = None

    def __init__(self, text=None):
        super().__init__(text)

        self.textChanged.connect(self.__handleTextChange)
        self.cursorPositionChanged.connect(self.__handleCursorChange)
        self.verticalScrollBar().valueChanged.connect(
            self.__handleVerticalScrollBarValueChange
        )
        self.horizontalScrollBar().valueChanged.connect(
            self.__handleHorizontalScrollBarValueChange
        )

        # self.selectionChanged.connect(self.__handleTextSelection)
        self.document().modificationChanged.connect(self.__handleModificationChange)
        self.document().contentsChange.connect(self.__handeContentChange)

        self.installEventFilter(self)

    # Events ---------------------------------
    def setOnHorizontalScrollBarValueChange(self, onHorizontalScrollBarValueChangeFunc):
        self.onHorizontalScrollBarValueChangeFunc = onHorizontalScrollBarValueChangeFunc

    def __handleHorizontalScrollBarValueChange(self, value):
        if self.onHorizontalScrollBarValueChangeFunc:
            self.onHorizontalScrollBarValueChangeFunc(self, value)

    def setOnVerticalScrollBarValueChange(self, onVerticalScrollBarValueChangeFunc):
        self.onVerticalScrollBarValueChangeFunc = onVerticalScrollBarValueChangeFunc

    def __handleVerticalScrollBarValueChange(self, value):
        if self.onVerticalScrollBarValueChangeFunc:
            self.onVerticalScrollBarValueChangeFunc(self, value)

    def setOnModificationChanged(self, onModificationChangeFunc):
        self.onModificationChangeFunc = onModificationChangeFunc

    def __handleModificationChange(self, changed):
        if self.onModificationChangeFunc:
            self.onModificationChangeFunc(self, changed)

    # Precisely check if content really changed
    def setOnContentChange(self, onContentChangeFunc):
        self.onContentChangeFunc = onContentChangeFunc

    def __handeContentChange(self, position, chars_removed, chars_added):
        if self.onContentChangeFunc:
            self.onContentChangeFunc(self, position, chars_removed, chars_added)

    def setOnCursorPositionChanged(self, onCursorPositionChangedFunc):
        self.onCursorPositionChangedFunc = onCursorPositionChangedFunc

    def __handleCursorChange(self):
        if self.onCursorPositionChangedFunc:
            self.onCursorPositionChangedFunc(self)

    def setOnKeyPress(self, onKeyPressChangeFunc):
        self.onKeyPressChangeFunc = onKeyPressChangeFunc

    def setOnTextChange(self, onTextChangedFunc):
        self.onTextChangedFunc = onTextChangedFunc

    def __handleTextChange(self):
        if self.onTextChangedFunc:
            self.onTextChangedFunc(self, self.getText())

    # def setOnSelection(self, onTextSelectionChangedFunc):
    #     self.onTextSelectionChangedFunc = onTextSelectionChangedFunc

    def __handleTextSelection(self):
        if self.onTextSelectionChangedFunc:
            self.onTextSelectionChangedFunc(self, self.selectedText())

    def keyPressEvent(self, event: QKeyEvent):
        if self.onKeyPressChangeFunc:
            self.onKeyPressChangeFunc(self, event)

        super().keyPressEvent(event)

    # --------------------------------- Events

    # Qt.ScrollBarAlwaysOff  # Hides scrollbar permanently
    # Qt.ScrollBarAlwaysOn   # Always shows scrollbar
    # Qt.ScrollBarAsNeeded   # Default (shows only when content overflows)

    def __decideScrollBehavior(self, scroll_policy):
        policy_mapping = {
            "overflow": Qt.ScrollBarPolicy.ScrollBarAsNeeded,
            "hidden": Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
            "always_on": Qt.ScrollBarPolicy.ScrollBarAlwaysOn,
        }

        if scroll_policy not in policy_mapping:
            raise ValueError(f"Invalid scroll policy type: {scroll_policy}.")

        return policy_mapping[scroll_policy]

    def setHorizontalScrollBarBehavior(self, prop):
        self.setHorizontalScrollBarPolicy(self.__decideScrollBehavior(prop))

    def setVerticalScrollBarBehavior(self, prop):
        self.setVerticalScrollBarPolicy(self.__decideScrollBehavior(prop))

    def setVerticalScrollBarValue(self, value):
        self.verticalScrollBar().setValue(value)

    def setHorizontalScrollBarValue(self, value):
        self.horizontalScrollBar().setValue(value)

    def setTextInteraction(self, interaction):
        interaction_map = {
            "none": Qt.TextInteractionFlag.NoTextInteraction,
            "text": Qt.TextInteractionFlag.TextBrowserInteraction,
            "editable": Qt.TextInteractionFlag.TextEditorInteraction,
            "read_only": Qt.TextInteractionFlag.TextBrowserInteraction,
        }

        try:
            self.setTextInteractionFlags(interaction_map[interaction.lower()])
        except KeyError:
            print(f"Invalid text interaction '{interaction}'.")

    def setFrameShape(self, frame_type):
        frame_map = {
            "none": QTextEdit.Shape.NoFrame,
            "box": QFrame.Shape.Box,
            "panel": QFrame.Shape.Panel,
            "winpanel": QFrame.Shape.WinPanel,
            "hline": QFrame.Shape.HLine,
            "vline": QFrame.Shape.VLine,
            "styledpanel": QFrame.Shape.StyledPanel,
        }

        try:
            super().setFrameShape(QTextEdit.NoFrame)
        except KeyError:
            print(f"Invalid frame type '{frame_type}'.")

    def setWrapMode(self, mode):
        mode_map = {
            "none": QTextEdit.LineWrapMode.NoWrap,
            "nowrap": QTextEdit.LineWrapMode.NoWrap,
            "widget": QTextEdit.LineWrapMode.WidgetWidth,
            "fixed": QTextEdit.LineWrapMode.FixedPixelWidth,
            "fixed_width": QTextEdit.LineWrapMode.FixedPixelWidth,
            "margin": QTextEdit.LineWrapMode.FixedColumnWidth,
            "column": QTextEdit.LineWrapMode.FixedColumnWidth,
        }

        try:
            self.setLineWrapMode(mode_map[mode.lower()])
        except KeyError:
            print(
                f"Invalid wrap mode '{mode}'. "
                f"Valid options: {', '.join(mode_map.keys())}"
            )

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

    def setToolTip(self, tooltip):
        super().setToolTip(tooltip)

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

    def clear(self):
        super().clear()

    def addCursorTable(self, rows, columns, padding, spacing):
        fmt = QTextTableFormat()

        fmt.setCellPadding(padding)

        fmt.setCellSpacing(spacing)

        # Inser the new table
        self.__getCursor().insertTable(rows, columns, fmt)

    # How much spacing on Tab button press
    def setTabSpacing(self, spacing):
        self.setTabStopDistance(spacing)

    def getLineCount(self):
        return self.document().lineCount()

    def getBlockNumber(self):
        return self.__getCursor().blockNumber()

    def getColumnNumber(self):
        return self.__getCursor().columnNumber()

    def __getCursor(self):
        return self.textCursor()

    def setFixedWidth(self, width):
        super().setFixedWidth(width)

    def setFixedHeight(self, height):
        super().setFixedHeight(height)

    def setTextSize(self, size):
        font = QFont()
        font.setPointSize(size)
        super().setFont(font)
        # self.setFontPointSize(int(size))

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

    def setTextAlignment(self, alignment):
        alignment_map = {
            "left": Qt.AlignmentFlag.AlignLeft,
            "right": Qt.AlignmentFlag.AlignRight,
            "bottom": Qt.AlignmentFlag.AlignBottom,
            "top": Qt.AlignmentFlag.AlignTop,
            "center": Qt.AlignmentFlag.AlignCenter,
            "hcenter": Qt.AlignmentFlag.AlignHCenter,
            "vcenter": Qt.AlignmentFlag.AlignVCenter,
            "justify": Qt.AlignmentFlag.AlignJustify,
        }

        try:
            self.setAlignment(alignment_map[alignment.lower()])
        except KeyError as e:
            raise ValueError(f"Invalid alignment: {alignment}") from e

    def setVerticalTextAlignment(self, format):
        fmt = self.currentCharFormat()

        if format == "normal":
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignNormal)

        elif format == "superscript":
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSuperScript)

        elif format == "subscript":
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSubScript)

        elif format == "middle":
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignMiddle)

        elif format == "top":
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignTop)

        elif format == "bottom":
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignBottom)

        elif format == "baseline":
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignBaseline)

        self.setCurrentCharFormat(fmt)

    def getVerticalTextAlignment(self):
        fmt = self.currentCharFormat()

        # And get the vertical alignment property
        align = fmt.verticalAlignment()

        # Toggle the state
        if align == QTextCharFormat.VerticalAlignment.AlignNormal:
            return "normal"

        elif align == QTextCharFormat.VerticalAlignment.AlignSuperScript:
            return "superscript"

        elif align == QTextCharFormat.VerticalAlignment.AlignSubScript:
            return "subscript"

        elif align == QTextCharFormat.VerticalAlignment.AlignMiddle:
            return "middle"

        elif align == QTextCharFormat.VerticalAlignment.AlignTop:
            return "top"

        elif align == QTextCharFormat.VerticalAlignment.AlignBottom:
            return "bottom"

        elif align == QTextCharFormat.VerticalAlignment.AlignBaseline:
            return "baseline"

    def removeBorder(self):
        super().setFrameShape(QFrame.Shape.NoFrame)

    def setPageSize(self, width, height):
        doc = self.document()

        doc.setPageSize(QSizeF(width, height))

    def setFocus(self):
        super().setFocus()

    def isModified(self):
        return self.document().isModified()

    def setModified(self, modified: bool):
        self.document().setModified(modified)

    def zoomIn(self, value):
        return super().zoomIn(value)

    def zoomOut(self, value):
        return super().zoomOut(value)

    def setTabSize(self, size):
        font_metrics = self.fontMetrics()
        space_width = font_metrics.horizontalAdvance(" ")
        tab_distance = space_width * size

        self.setTabStopDistance(tab_distance)

    """
            What is a "Block"?
            
    A block is essentially a paragraph or a line in the document.

    Every time you press Enter/Return, you create a new block.

    Even an empty document has 1 block (an empty line).
    """

    def getBlockCount(self):
        return self.document().blockCount()
