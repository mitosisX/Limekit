from PySide6.QtGui import QIcon, QStandardItem, QIcon
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QTreeWidget
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.core.engine.destroyer import destroy_engine
from limekit.framework.components.base.base_widget import BaseWidget


class TreeViewItem(QStandardItem, EnginePart):
    onClickFunc = None

    def __init__(self, text):
        super().__init__(text)
        # BaseWidget.__init__(self, widget=self)

    def setIcon(self, icon):
        if isinstance(icon, str):
            super().setIcon(QIcon(icon))
            return

        super().setIcon(icon)

    def setEditable(self, editable):
        super().setEditable(editable)

    def addRow(self, rows):
        self.appendRow([row for row in rows.values()])

    def setExpanded(self, expanded):
        super().setExpanded(expanded)
