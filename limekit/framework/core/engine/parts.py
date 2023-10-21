# Any class to be intantiated in the engine needs to inherit this


class EnginePart:
    """
    If name hasn't been assigned, that signifies that the class name (class.__name__)
    should be used instead
    """

    name = ""
    premium = False  # To be used for license restrictions

    def __str__(self):
        return "Limekit Lua Framework"
