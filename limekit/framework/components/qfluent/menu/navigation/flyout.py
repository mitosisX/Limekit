from limekit.framework.core.engine.app_engine import EnginePart
from qfluentwidgets import Flyout, FlyoutAnimationType


class FluentFlyout(Flyout, EnginePart):
    name = "Flyout"
    window = None
    view = None

    def __init__(self, window, view) -> None:
        super().__init__(view)
        self.window = window
        self.view = view

    def show(self, target):
        self.make(self.view, target, self.window, FlyoutAnimationType.FADE_IN)
