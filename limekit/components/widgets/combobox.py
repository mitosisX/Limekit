import lupa

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QComboBox
from limekit.engine.parts import EnginePart
from PySide6.QtWidgets import QSizePolicy
from limekit.utils.converters import Converter

# setMaxCount - sets maximum ComboBox items limit

# QComboBox.NoInsert	No insert
# QComboBox.InsertAtTop	Insert as first item
# QComboBox.InsertAtCurrent	Replace currently selected item
# QComboBox.InsertAtBottom	Insert after last item
# QComboBox.InsertAfterCurrent	Insert after current item
# QComboBox.InsertBeforeCurrent	Insert before current item
# QComboBox.InsertAlphabetically	Insert in alphabetical order


class ComboBox(QComboBox, EnginePart):
    onCurrentIndexChangedFunc = None
    onWidgetActivatedFunc = None

    def __init__(self, items=None):
        super().__init__()

        if items:
            self.setItems(items)

        self.currentIndexChanged.connect(self.__handleCurrentIndexChange)
        # self.activated.connect(self.__handleWidgetActivated)

    def setOnItemSelect(self, onCurrentIndexChangedFunc):
        self.onCurrentIndexChangedFunc = onCurrentIndexChangedFunc

    def setOnActive(self, onWidgetActivatedFunc):
        self.onWidgetActivatedFunc = onWidgetActivatedFunc

    def __handleCurrentIndexChange(self):
        if self.onCurrentIndexChangedFunc:
            self.onCurrentIndexChangedFunc(
                self, self.currentText(), self.getCurrentIndex()
            )

    def __handleWidgetActivated(self):
        if self.onWidgetActivatedFunc:
            self.onWidgetActivatedFunc(self)

    def getCurrentIndex(self):
        return self.currentIndex()

    def getText(self):
        return self.currentText()

    """
    This displays an image and text on the combobox
    [images('image'), 'text']
    """

    # def addImageItem(self, data):
    #     icon = QIcon(data[0])
    #     text = data[1]

    #     self.addItem(icon, text)

    def addImageItem(self, data):
        values = data.values()
        text = values[1]
        icon = QIcon(values[2])

        super().addItem(icon, text)

    def addImageItems(self, data):
        for values in data.values():
            text = values[1]
            icon = QIcon(values[2])

            super().addItem(icon, text)

    # QComboBox.NoInsert	Performs no insert.
    # QComboBox.InsertAtTop	Inserts as first item.
    # QComboBox.InsertAtCurrent	Replaces the currently selected item.
    # QComboBox.InsertAtBottom	Inserts after the last item.
    # QComboBox.InsertAfterCurrent	Inserts after the current item.
    # QComboBox.InsertBeforeCurrent	Inserts before the current item.
    # QComboBox.InsertAlphabetically	Inserts in alphabetical order.
    def setInsertOrder(self, order):
        self.setInsertPolicy(QComboBox.InsertPolicy.InsertAlphabetically)

    def setItems(self, items):
        items = items.values() if lupa.lua_type(items) == "table" else items

        for item in items:
            self.addItem(item)

    def addItem(self, item):
        super().addItem(item)

    def addItems(self, data):
        data_ = ""

        try:
            data_ = list(data.values())
        except AttributeError:
            data_ = data

        super().addItems(data_)

    def setEditable(self, editable):
        super().setEditable(editable)

    def setResizeRule(self, horizontal, vertical):
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

    def setMinContentLength(self, length):
        self.setMinimumContentsLength(length)

    def setMinWidth(self, width):
        self.setMinimumWidth(width)

    def setMaxWidth(self, width):
        self.setMaximumWidth(width)

    def setMinHeight(self, height):
        self.setMinimumHeight(height)

    def setMaxHeight(self, height):
        self.setMaximumHeight(height)

    def getCurrentText(self):
        return self.currentText()

    def setCurrentIndex(self, index):
        super().setCurrentIndex(index)

    def setFixedWidth(self, width):
        super().setFixedWidth(width)

    def setFixedHeight(self, height):
        super().setFixedHeight(height)
