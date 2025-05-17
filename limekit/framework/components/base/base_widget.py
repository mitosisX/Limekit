from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import QSize


class BaseWidget:
    def __init__(self, widget):
        self.widget = widget

    def enable(self):
        self.widget.setEnabled(True)

    def disable(self):
        self.widget.setEnabled(False)

    def setBackgroundColor(self, color):
        self.widget.setStyleSheet(f"background-color: {color};")

    def setFixedSizes(self, width, height):
        self.widget.setFixedSize(QSize(width, height))

    def setTextColor(self, color):
        self.widget.setStyleSheet(f"color: {color};")

    # Also acts as the padding
    def setMargins(self, left, top, right, bottom):
        self.widget.setContentsMargins(left, top, right, bottom)

    def setSize(self, width, height):
        self.widget.resize(width, height)

    def setWidth(self, width):
        self.widget.resize(width, self.height())

    def setHeight(self, height):
        self.widget.resize(self.width(), height)

    def setMinHeight(self, height):
        self.widget.setMinimumHeight(height)

    def setMaxHeight(self, height):
        self.widget.setMaximumHeight(height)

    def setMinWidth(self, width):
        self.widget.setMinimumWidth(width)

    def setMaxWidth(self, width):
        self.widget.setMaximumWidth(width)

    def setVisibility(self, visibility):
        self.widget.setVisible(visibility)

    def setResizeRule(self, horizontal: str, vertical: str):
        policies = {
            "fixed": QSizePolicy.Policy.Fixed,  # ignores all size changing
            "expanding": QSizePolicy.Policy.Expanding,  # makes sure to expand to all available spaces
            "ignore": QSizePolicy.Policy.Ignored,  # does nothing
            "maximum": QSizePolicy.Policy.Maximum,
            "minimum": QSizePolicy.Policy.Minimum,
            "minimumexpanding": QSizePolicy.Policy.MinimumExpanding,
        }

        horizontal = horizontal.lower()
        vertical = vertical.lower()

        if (horizontal in policies) and (vertical in policies):
            size_policy = QSizePolicy(policies.get(horizontal), policies.get(vertical))
            self.widget.setSizePolicy(size_policy)

    def setLocation(self, x, y):
        self.widget.move(x, y)
