from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QComboBox
from limekit.framework.core.engine.parts import EnginePart
import lupa

# setMaxCount - sets maximum ComboBox items limit

# QComboBox.NoInsert	No insert
# QComboBox.InsertAtTop	Insert as first item
# QComboBox.InsertAtCurrent	Replace currently selected item
# QComboBox.InsertAtBottom	Insert after last item
# QComboBox.InsertAfterCurrent	Insert after current item
# QComboBox.InsertBeforeCurrent	Insert before current item
# QComboBox.InsertAlphabetically	Insert in alphabetical order
from lupa import LuaRuntime


class ComboBox(EnginePart, QComboBox):
    def __init__(self, items):
        super().__init__()

        if items:
            self.addDataItems(items)

    def onItemSelected(self, func):
        self.currentIndexChanged.connect(lambda: func(self, self.currentText()))

    def getSelectedItem(self):
        return self.currentText()

    """
    This displays an image and text on the combobox
    [images('image'), 'text']
    """

    def addImageItem(self, data):
        icon = QIcon(data[0])
        text = data[1]

        self.addItem(icon, text)

    def addImageItems(self, data):
        for values in data.values():
            text = values[1]
            icon = QIcon(values[2])

            self.addItem(icon, text)

    def addDataItems(self, data):
        data_ = ""

        try:
            data_ = list(data.values())
        except AttributeError:
            data_ = data

        self.addItems(data_)
