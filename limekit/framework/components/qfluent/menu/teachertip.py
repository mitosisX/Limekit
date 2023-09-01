from limekit.framework.core.engine.app_engine import EnginePart
from qfluentwidgets import TeachingTipView, TeachingTipTailPosition, TeachingTip


class PopupTooltip(EnginePart):
    target = None
    title = ""
    content = ""
    image = ""

    # var:target is the widget that the popup displays on
    def __init__(self, target, title, content, image):
        self.target = target
        self.title = title
        self.content = content
        self.image = image

    def show(self):
        position = TeachingTipTailPosition.BOTTOM
        view = TeachingTipView(
            icon=None,
            title=self.title,
            content=self.content,
            image=self.image,
            isClosable=True,
            tailPosition=position,
        )

        w = TeachingTip.make(
            target=self.target,
            view=view,
            duration=-1,
            tailPosition=position,
            parent=self,
        )
