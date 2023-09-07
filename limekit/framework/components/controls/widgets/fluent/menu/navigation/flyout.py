from limekit.framework.core.engine.app_engine import EnginePart
from qfluentwidgets import Flyout, FlyoutAnimationType


# a Popup with MenuItems next to them
class FluentFlyout(Flyout, EnginePart):
    name = "Flyout"
    window = None
    view = None

    def __init__(self, window, view) -> None:
        super().__init__(view)
        self.window = window
        self.view = view

    def show(self, target, fly_animation: str = "pullup"):
        animation_ = fly_animation.lower()
        animation_type = FlyoutAnimationType.DROP_DOWN

        if animation_ == "dropdown":
            animation_type = FlyoutAnimationType.DROP_DOWN

        elif animation_ == "fadein":
            animation_type = FlyoutAnimationType.FADE_IN

        elif animation_ == "pullup":
            animation_type = FlyoutAnimationType.PULL_UP

        elif animation_ == "slideleft":
            animation_type = FlyoutAnimationType.SLIDE_LEFT

        elif animation_ == "slideright":
            animation_type = FlyoutAnimationType.SLIDE_RIGHT

        self.make(self.view, target, self.window, animation_type)

    def getAnimations(self):
        return ["dropdown", "fadein", "pullup", "slideleft", "slideright"]
