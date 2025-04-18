from PySide6.QtWidgets import QInputDialog
from limekit.framework.core.engine.parts import EnginePart
import lupa


class ItemInputDialog(EnginePart):
    name = "__itemInputDialog"

    @classmethod
    def show(cls, parent, title, label, items, index):
        item, dialog = QInputDialog.getItem(
            parent,
            title,
            label,
            items.values() if lupa.lua_type(items) == "table" else items,
            index,  # From the list - which one to display upon show
            False,
        )

        return item if dialog else None
