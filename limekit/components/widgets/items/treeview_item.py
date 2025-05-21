import lupa
from PySide6.QtGui import QIcon, QStandardItem, QIcon
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QTreeWidget
from limekit.engine.parts import EnginePart
from limekit.engine.lifecycle.shutdown import destroy_engine
from limekit.components.base.base_widget import BaseWidget


class TreeViewItem(QStandardItem, EnginePart):
    onClickFunc = None

    def __init__(self, text):
        super().__init__(text)

    def setIcon(self, icon):
        if isinstance(icon, str):
            super().setIcon(QIcon(icon))
            return

        super().setIcon(icon)

    def setEditable(self, editable):
        super().setEditable(editable)

    def addRow(self, rows):
        # If the arg are passed as a lua table {TreeViewItem(), TreeViewItem(), ...}
        if lupa.lua_type(rows) == "table":
            # self.appendRows([row for row in rows.values()])
            self.appendRows(list(rows.values()))
        else:
            self.appendRow(rows)

    def setExpanded(self, expanded):
        super().setExpanded(expanded)
