from PySide6.QtWidgets import QStyleFactory
from limekit.engine.lifecycle.app import App
from limekit.engine.parts import EnginePart
from limekit.utils.converters import Converter


class AppStyles(EnginePart):
    name = "__appStyles"

    """
    Platform-dependent styles: Fusion, etc
    """

    @classmethod
    def setStyle(cls, style):
        App.app.setStyle(style)

    @classmethod
    def getStyles(cls):
        return Converter.to_lua_table(QStyleFactory.keys())
