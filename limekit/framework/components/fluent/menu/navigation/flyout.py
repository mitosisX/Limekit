from limekit.framework.core.engine.parts import EnginePart
from qfluentwidgets import Flyout, FlyoutAnimationType


# a Popup with MenuItems next to them
class FluentFlyout(Flyout, EnginePart):
    name = "Flyout"
    window = None
    view = None

    def __init__(self, window, view):
        super().__init__(view)
        self.window = window
        self.view = view

    def showSimple(self):
        Flyout.create(
            icon=InfoBarIcon.SUCCESS,
            title="Lesson 3",
            content=self.tr("Believe in the spin, just keep believing!"),
            target=self.simpleFlyoutButton,
            parent=self.window(),
        )

    def show(self, target, fly_animation="pullup"):
        animation_map = {
            "dropdown": FlyoutAnimationType.DROP_DOWN,
            "fadein": FlyoutAnimationType.FADE_IN,
            "pullup": FlyoutAnimationType.PULL_UP,
            "slideleft": FlyoutAnimationType.SLIDE_LEFT,
            "slideright": FlyoutAnimationType.SLIDE_RIGHT,
        }

        animation_type = animation_map.get(
            fly_animation.lower(), FlyoutAnimationType.PULL_UP
        )
        self.make(self.view, target, self.window, animation_type)

        # animation_ = fly_animation.lower()
        # animation_type = FlyoutAnimationType.PULL_UP

        # if animation_ == "dropdown":
        #     animation_type = FlyoutAnimationType.DROP_DOWN

        # elif animation_ == "fadein":
        #     animation_type = FlyoutAnimationType.FADE_IN

        # elif animation_ == "pullup":
        #     animation_type = FlyoutAnimationType.PULL_UP

        # elif animation_ == "slideleft":
        #     animation_type = FlyoutAnimationType.SLIDE_LEFT

        # elif animation_ == "slideright":
        #     animation_type = FlyoutAnimationType.SLIDE_RIGHT

        # self.make(self.view, target, self.window, animation_type)

    def getAnimations(self):
        return ["dropdown", "fadein", "pullup", "slideleft", "slideright"]
