from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.core.engine.destroyer import destroy_engine
from limekit.framework.components.base.base_widget import BaseWidget


class TreeWidget(QTreeWidget, BaseWidget, EnginePart):
    onClickFunc = None

    def __init__(self):
        super().__init__()
        BaseWidget.__init__(self, widget=self)

        # self.clicked.connect(self.__handleOnClick)

    def __handleOnClick(self):
        if self.onClickFunc:
            try:
                self.onClickFunc(self)
            except Exception as ex:
                print(ex)
                destroy_engine()

    def addData(self):
        category_1 = QTreeWidgetItem(
            self, ["Apples", "Edible fruit produced by an apple tree"]
        )

    def setHeaders(self, headers):
        self.setHeaderLabels(headers.values())

    def setMaxColumns(self, columns):
        self.setColumnCount(columns)

    def setColumnWidth(self, column, width):
        super().setColumnWidth(column, width)
