from PySide6.QtGui import QIcon, QStandardItemModel
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QTreeView, QStyle
from limekit.engine.parts import EnginePart
from limekit.engine.lifecycle.shutdown import destroy_engine
from limekit.components.widgets.items.treeview_item import TreeViewItem
from limekit.components.base.base_widget import BaseWidget


class TreeView(BaseWidget, QTreeView, EnginePart):
    onClickFunc = None

    def __init__(self):
        super().__init__()

        self.model = QStandardItemModel()
        self.setModel(self.model)

    def setMaxColumns(self, num):
        self.setColumnCount(num)

    def setHeaders(self, headers):
        self.model.setHorizontalHeaderLabels(headers.values())

    def setHeaderHidden(self, visible):
        super().setHeaderHidden(visible)

    def addRow(self, row):
        self.model.appendRow(row)

    def setColumnWidth(self, column, width):
        super().setColumnWidth(column, width)

    def setTreeItemExpanded(self, x, y):
        self.expand(self.model(x, y))

    def expandAll(self):
        super().expandAll()

    # This clears the entire tree view, including the headers
    def clear(self):
        self.model.clear()

    # Half baked
    def getRecommendedIconSizes(self):
        # Get system-recommended sizes
        small_icon = self.style().pixelMetric(QStyle.PM_SmallIconSize)
        large_icon = self.style().pixelMetric(QStyle.PM_LargeIconSize)

        return {
            "small": QSize(small_icon, small_icon),
            "large": QSize(large_icon, large_icon),
        }
