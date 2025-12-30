from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Qt
from limekit.engine.parts import EnginePart
from limekit.components.base.widget_base import BaseWidget


class TreeWidget(BaseWidget, QTreeWidget, EnginePart):
    """A tree widget for displaying hierarchical data."""

    onItemClickFunc = None
    onItemDoubleClickFunc = None

    def __init__(self):
        super().__init__()
        self.itemClicked.connect(self.__handleItemClick)
        self.itemDoubleClicked.connect(self.__handleItemDoubleClick)

    def setOnItemClick(self, func):
        self.onItemClickFunc = func

    def __handleItemClick(self, item, column):
        if self.onItemClickFunc:
            self.onItemClickFunc(TreeItem.wrap(item))

    def setOnItemDoubleClick(self, func):
        self.onItemDoubleClickFunc = func

    def __handleItemDoubleClick(self, item, column):
        if self.onItemDoubleClickFunc:
            self.onItemDoubleClickFunc(TreeItem.wrap(item))

    def setHeaderLabels(self, labels):
        """Set column headers from a Lua table."""
        header_list = list(labels.values())
        self.setColumnCount(len(header_list))
        super().setHeaderLabels(header_list)

    def setColumnWidth(self, column, width):
        """Set the width of a specific column."""
        super().setColumnWidth(column, width)

    def addTopItem(self, item):
        """Add a top-level item to the tree."""
        if isinstance(item, TreeItem):
            self.addTopLevelItem(item._item)
        else:
            self.addTopLevelItem(item)

    def getCurrentItem(self):
        """Get the currently selected item."""
        item = self.currentItem()
        if item:
            return TreeItem.wrap(item)
        return None

    def clear(self):
        """Clear all items from the tree."""
        super().clear()

    def expandAll(self):
        """Expand all items in the tree."""
        super().expandAll()

    def collapseAll(self):
        """Collapse all items in the tree."""
        super().collapseAll()


class TreeItem(EnginePart):
    """A tree item for use with TreeWidget."""

    def __init__(self, texts):
        """Create a tree item with the given column texts (Lua table)."""
        text_list = list(texts.values())
        self._item = QTreeWidgetItem(text_list)

    @classmethod
    def wrap(cls, qt_item):
        """Wrap an existing QTreeWidgetItem."""
        wrapper = cls.__new__(cls)
        wrapper._item = qt_item
        return wrapper

    def addChild(self, child):
        """Add a child item."""
        if isinstance(child, TreeItem):
            self._item.addChild(child._item)
        else:
            self._item.addChild(child)

    def setText(self, column, text):
        """Set text for a specific column."""
        self._item.setText(column, str(text))

    def getText(self, column):
        """Get text from a specific column."""
        return self._item.text(column)

    def setExpanded(self, expanded):
        """Set whether the item is expanded."""
        self._item.setExpanded(expanded)

    def isExpanded(self):
        """Check if the item is expanded."""
        return self._item.isExpanded()

    def setIcon(self, column, icon):
        """Set an icon for a specific column."""
        from PySide6.QtGui import QIcon
        self._item.setIcon(column, QIcon(icon))

    def childCount(self):
        """Get the number of children."""
        return self._item.childCount()

    def child(self, index):
        """Get a child item by index."""
        qt_child = self._item.child(index)
        if qt_child:
            return TreeItem.wrap(qt_child)
        return None

    def parent(self):
        """Get the parent item."""
        qt_parent = self._item.parent()
        if qt_parent:
            return TreeItem.wrap(qt_parent)
        return None
