from limekit.framework.core.engine.app_engine import EnginePart
from playsound import playsound


class Sound(EnginePart):
    name = "__sound"

    @classmethod
    def play_sound(cls, path):
        playsound(path)
