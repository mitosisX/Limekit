from PySide6.QtWidgets import QWidget, QSizePolicy


class BaseWidget:
    def __init__(self, widget: QWidget):
        self.widget = widget

    # Also acts as the padding
    def setMargins(self, left, top, right, bottom):
        self.widget.setContentsMargins(left, top, right, bottom)

    def setSize(self, width, height):
        self.widget.resize(width, height)

    def setMinHeight(self, height):
        self.widget.setMinimumHeight(height)

    def setMaxHeight(self, height):
        self.widget.setMaximumHeight(height)

    def setMinWidth(self, width):
        self.widget.setMinimumWidth(width)

    def setMaxWidth(self, width):
        self.widget.setMaximumWidth(width)

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
            self.widget.setSizePolicy(size_policy)
