from limekit.engine.parts import EnginePart
from playsound import playsound


class Sound(EnginePart):
    name = "__sound"

    @staticmethod
    def play_sound(path):
        playsound(path)
