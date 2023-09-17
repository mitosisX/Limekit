from limekit.framework.core.engine.parts import EnginePart
from qfluentwidgets import FlyoutView, Flyout


# Displays a popup with an Image, title, content + a close button for dismissing
class ImagePopup(EnginePart):
    title = ""
    content = ""
    image = ""

    def __init__(self, title, content, image):
        self.title = title
        self.content = content
        self.image = image

    def show(self, widget, window):
        view = FlyoutView(
            title=self.title, content=self.content, image=self.image, isClosable=True
        )

        w = Flyout.make(view, widget, window)
        view.closed.connect(w.close)
