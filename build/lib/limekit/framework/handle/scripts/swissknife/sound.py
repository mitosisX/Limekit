from limekit.framework.core.engine.parts import EnginePart
from playsound import playsound


class Sound(EnginePart):
    name = "__sound"

    @classmethod
    def play_sound(cls, path):
        playsound(path)
