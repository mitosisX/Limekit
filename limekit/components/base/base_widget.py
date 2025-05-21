from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import QSize


class BaseWidget:
    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)

    def setBackgroundColor(self, color):
        self.setStyleSheet(f"background-color: {color};")

    def setFixedSize(self, width, height):
        super().setFixedSize(QSize(width, height))

    def setStyle(self, style):
        self.setStyleSheet(style)

    # Also acts as the padding
    def setMargins(self, left, top, right, bottom):
        self.setContentsMargins(left, top, right, bottom)

    def setSize(self, width, height):
        self.resize(width, height)

    def setWidth(self, width):
        self.resize(width, self.height())

    def setHeight(self, height):
        self.resize(self.width(), height)

    def setMinHeight(self, height):
        self.setMinimumHeight(height)

    def setMaxHeight(self, height):
        self.setMaximumHeight(height)

    def setMinWidth(self, width):
        self.setMinimumWidth(width)

    def setMaxWidth(self, width):
        self.setMaximumWidth(width)

    def setVisibility(self, visibility):
        self.setVisible(visibility)

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
            self.setSizePolicy(size_policy)

    def setLocation(self, x, y):
        self.move(x, y)
