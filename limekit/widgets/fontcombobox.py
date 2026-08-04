"""Font-picker combo box.

`currentIndex` can't be a `Prop`: it is 0-indexed in Qt, and translating
that requires a real wrapper -- the same reason `Tab.setCurrentIndex` and
`ListBox.setCurrentRow` are hand-written instead of declarative (see
tab.py). `setFont` deliberately overrides `QWidget.setFont(QFont)` with a
string-accepting version, the same shape as `TextField.setText` overriding
`QTextEdit.setText`.
"""

from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QFontComboBox

from limekit.kernel.bridge.convert import as_sequence
from limekit.kernel.bridge.guard import guard
from limekit.kernel.coerce import LuaIndex
from limekit.kernel.spec import Prop
from limekit.widgets.base import LimeWidget


class FontComboBox(LimeWidget, QFontComboBox):
    __lime__ = "ui.FontComboBox"

    currentFont = Prop(object, qt=("currentFont", "setCurrentFont"))

    def __init__(self):
        super().__init__()
        self._onItemSelect = None
        self.currentIndexChanged.connect(self._handleCurrentIndexChange)

    def getText(self):
        return self.currentText()

    def getCurrentIndex(self):
        return self.currentIndex() + 1

    def setCurrentIndex(self, index):
        super().setCurrentIndex(LuaIndex(index))
        return self

    def setFont(self, font_string):
        """Overrides QWidget.setFont(QFont) with a string-accepting version,
        e.g. `combo:setFont("Arial,10,-1,5,50,0,0,0,0,0")`."""
        font = QFont()
        font.fromString(str(font_string))
        super().setFont(font)
        return self

    def addImageItem(self, icon, text):
        self.addItem(QIcon(icon), str(text))
        return self

    def addItem(self, text):
        """Qt native re-exposed so it chains like every builder method."""
        super().addItem(str(text))
        return self

    def addItems(self, items):
        super().addItems([str(i) for i in as_sequence(items)])
        return self

    def setOnItemSelect(self, handler):
        self._onItemSelect = guard(handler, widget="FontComboBox", event="onItemSelect")
        return self

    def _handleCurrentIndexChange(self, index):
        if self._onItemSelect:
            self._onItemSelect(self, self.currentText(), index + 1)
