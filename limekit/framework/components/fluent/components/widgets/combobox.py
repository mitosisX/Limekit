import lupa
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.handle.scripts.swissknife.converters import Converter
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSizePolicy
from qfluentwidgets import ComboBox

# setMaxCount - sets maximum ComboBox items limit


class FComboBox(ComboBox, EnginePart):
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
