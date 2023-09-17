from limekit.framework.core.engine.parts import EnginePart
import emoji


class Emoji(EnginePart):
    name = "__emoji"

    @classmethod
    def get(cls, emoji_str):
        return emoji.emojize(emoji_str, language="alias")
