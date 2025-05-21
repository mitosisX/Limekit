from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QWidget
from limekit.engine.parts import EnginePart
from limekit.components.base.base_widget import BaseWidget


class Scroller(BaseWidget, QScrollArea, EnginePart):
    onScrollFunc = None

    def __init__(self):
        super().__init__(parent=None)

        self.vertical_scrollbar = self.verticalScrollBar()
        self.horizontal_scrollbar = self.horizontalScrollBar()

        self.parent_widget = QWidget()
        self.setWidget(self.parent_widget)

        self.setHorizontalScrollBarBehavior("overflow")
        self.setVerticalScrollBarBehavior("overflow")
        self.setResizable(True)

        self.verticalScrollBar().valueChanged.connect(self.__handleScroll)

    def setOnScroll(self, onScrollFunc):
        self.onScrollFunc = onScrollFunc

    def __handleScroll(self, value):
        if self.onScrollFunc:
            self.onScrollFunc(self, value)

    # Determine whether the widget can be resized to accomodate the content
    def setResizable(self, resizable):
        self.setWidgetResizable(resizable)

    def maxVerticalScroll(self):
        max_scroll_value = self.vertical_scrollbar.maximum()

        return max_scroll_value

    def minVerticalScroll(self):
        min_scroll_value = self.vertical_scrollbar.minimum()

        return min_scroll_value

    def maxHorizontalScroll(self):
        max_scroll_value = self.horizontal_scrollbar.maximum()

        return max_scroll_value

    def minHorizontalScroll(self):
        min_scroll_value = self.horizontal_scrollbar.minimum()

        return min_scroll_value

    def setChild(self, child):
        self.setWidget(child)

    def setLayout(self, layout):
        self.parent_widget.setLayout(layout)

    def setResizable(self, resizable):
        self.setWidgetResizable(resizable)

    def __decideScrollBehavior(self, prop):
        policy = Qt.ScrollBarPolicy.ScrollBarAsNeeded

        if prop == "overflow":
            policy = Qt.ScrollBarPolicy.ScrollBarAsNeeded
        elif prop == ("hidden"):
            policy = Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        elif prop == ("alwayson"):
            policy = Qt.ScrollBarPolicy.ScrollBarAlwaysOn

        return policy

    def setHorizontalScrollBarBehavior(self, prop):
        self.setHorizontalScrollBarPolicy(self.__decideScrollBehavior(prop))

    def setVerticalScrollBarBehavior(self, prop):
        self.setVerticalScrollBarPolicy(self.__decideScrollBehavior(prop))
