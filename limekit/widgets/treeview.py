"""Hierarchical list widget.

1.x split this across two files that disagreed with each other:
`tree_widget.py` (a `QTreeWidget` plus a `TreeItem` wrapper -- complete and
working) and `treewidget.py` (a `QTreeView` over a `QStandardItemModel`,
explicitly marked "Half baked" in its own comments and genuinely broken --
`setTreeItemExpanded` called `self.model(x, y)` as though the model were
callable rather than indexable, and `setHeaders` piped a raw Lua table
straight into `setHorizontalHeaderLabels` with no coercion). This module
keeps the `QTreeWidget` design from `tree_widget.py` under the requested
names (`TreeView`, `TreeViewItem`) and drops the `QStandardItemModel`
version entirely rather than reconciling two incompatible object models.
"""

from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem

from limekit.kernel.bridge.convert import as_sequence
from limekit.kernel.coerce import Icon, LuaIndex
from limekit.kernel.declarative import LimeObject
from limekit.kernel.spec import Event, Prop
from limekit.widgets.base import LimeWidget, _to_int
from limekit.kernel.registry import registry


class TreeViewItem(LimeObject, QTreeWidgetItem):
    __lime__ = "ui.TreeViewItem"

    expanded = Prop(bool, qt=("isExpanded", "setExpanded"))

    def __init__(self, texts=None):
        super().__init__([str(t) for t in as_sequence(texts)])

    def setText(self, column, text):
        super().setText(LuaIndex(column), str(text))
        return self

    def getText(self, column):
        return self.text(LuaIndex(column))

    def setIcon(self, column, icon):
        super().setIcon(LuaIndex(column), Icon(icon))
        return self

    def addChild(self, child):
        super().addChild(child)
        return self

    def getChildAt(self, index):
        return self.child(LuaIndex(index))

    def getChildCount(self):
        return self.childCount()

    def getParent(self):
        return self.parent()


class TreeView(LimeWidget, QTreeWidget):
    __lime__ = "ui.TreeView"

    headerHidden = Prop(bool, qt=("isHeaderHidden", "setHeaderHidden"))

    onItemClick = Event("itemClicked", passes_self=True,
                        params=(("item", "any"), ("column", "integer")),
                        indices=("column",),
                        doc="Fired when an item is clicked. column is 1-based.")
    onItemDoubleClick = Event("itemDoubleClicked", passes_self=True,
                              params=(("item", "any"), ("column", "integer")),
                              indices=("column",),
                              doc="Fired when an item is double-clicked. column is 1-based.")

    def __init__(self):
        super().__init__()

    def setHeaderLabels(self, labels):
        header_list = [str(h) for h in as_sequence(labels)]
        self.setColumnCount(len(header_list))
        super().setHeaderLabels(header_list)
        return self

    def setColumnWidth(self, column, width):
        super().setColumnWidth(LuaIndex(column), _to_int(width, "width"))
        return self

    def addTopItem(self, item):
        """Qt native (`addTopLevelItem`) re-exposed so it chains."""
        self.addTopLevelItem(item)
        return self

    def getTopItemAt(self, index):
        return self.topLevelItem(LuaIndex(index))

    def getTopItemCount(self):
        return self.topLevelItemCount()

    def getCurrentItem(self):
        return self.currentItem()

    def clear(self):
        super().clear()
        return self

    def expandAll(self):
        super().expandAll()
        return self

    def collapseAll(self):
        super().collapseAll()
        return self


# `TreeWidget` is 1.x's other name for a tree. 1.x shipped two
# implementations: components/widgets/tree_widget.py (QTreeWidget-based,
# complete) and components/widgets/treewidget.py (QTreeView +
# QStandardItemModel, self-labelled "Half baked", and calling
# self.model(x, y) as though the model attribute were callable). This is a
# port of the working one, registered under both names so a demo written
# against either keeps resolving.
registry.register("ui.TreeWidget", TreeView)
