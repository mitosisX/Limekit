# QQuickWidget

from limekit.engine.parts import EnginePart
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtCore import QUrl
from limekit.components.base.widget_base import BaseWidget


class QmlWidget(BaseWidget, QQuickWidget, EnginePart):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)

    def setSource(self, source):
        super().setSource(QUrl.fromLocalFile(source))

    def setBridge(self, name, bridge):
        self.engine().rootContext().setContextProperty(name, bridge)

    # def setResizeMode(self, mode):
    #     QQuickWidget.ResizeMode.
    #     return super().setResizeMode(mode)
