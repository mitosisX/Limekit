import lupa

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QComboBox
from limekit.framework.core.engine.parts import EnginePart
from PySide6.QtWidgets import QSizePolicy

# setMaxCount - sets maximum ComboBox items limit

# QComboBox.NoInsert	No insert
# QComboBox.InsertAtTop	Insert as first item
# QComboBox.InsertAtCurrent	Replace currently selected item
# QComboBox.InsertAtBottom	Insert after last item
# QComboBox.InsertAfterCurrent	Insert after current item
# QComboBox.InsertBeforeCurrent	Insert before current item
# QComboBox.InsertAlphabetically	Insert in alphabetical order
from limekit.framework.handle.scripts.swissknife.converters import Converter


class ComboBox(QComboBox, EnginePart):
    onCurrentIndexChangedFunc = None

    def __init__(self, items=None):
        super().__init__()

        if items:
            self.setItems(items)

        self.currentIndexChanged.connect(self.__handleCurrentIndexChange)

    def setOnItemSelected(self, onCurrentIndexChangedFunc):
        self.onCurrentIndexChangedFunc = onCurrentIndexChangedFunc

    def __handleCurrentIndexChange(self):
        if self.onCurrentIndexChangedFunc:
            self.onCurrentIndexChangedFunc(
                self, self.currentText(), self.getCurrentIndex()
            )

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
