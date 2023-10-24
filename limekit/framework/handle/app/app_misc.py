from PySide6.QtWidgets import QStyleFactory
from limekit.framework.core.runner.app import App
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.handle.scripts.swissknife.converters import Converter


class AppMisc(EnginePart):
    name = "__appMisc"

    """
    Platform-dependent Styles obtained from getStyles() method
    """

    @classmethod
    def setStyle(cls, style):
        App.app.setStyle(style)

    @classmethod
    def getStyles(cls):
        return Converter.to_lua_table(QStyleFactory.keys())
