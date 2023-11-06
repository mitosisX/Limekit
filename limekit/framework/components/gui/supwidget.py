from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QSizePolicy


class SupWidget:
    def __init__(self, child: QWidget):
        self.child = child

    def setResizeRule(self, horizontal: str, vertical: str):
        policies = {
            "fixed": QSizePolicy.Policy.Fixed,  # ignores all size changing
            "expanding": QSizePolicy.Policy.Expanding,  # makes sure to expand to all available spaces
            "ignore": QSizePolicy.Policy.Ignored,  # does nothing
        }

        horizontal = horizontal.lower()
        vertical = vertical.lower()

        if (horizontal in policies) and (vertical in policies):
            size_policy = QSizePolicy(policies.get(horizontal), policies.get(vertical))
            self.child.setSizePolicy(size_policy)
