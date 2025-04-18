from PySide6.QtWidgets import QInputDialog
from limekit.framework.core.engine.parts import EnginePart


class IntegerInputDialog(EnginePart):
    name = "__integerInputDialog"

    @classmethod
    def show(
        cls,
        parent,
        title,
        label,
        value,
        minValue,
        maxValue,
        step,  # Step: number of leading zeros, which is 2 by default (1.00)
    ):
        value, dialog = QInputDialog.getInt(
            parent, title, label, value, minValue, maxValue, step
        )

        return value if dialog else None
