from qfluentwidgets import isDarkTheme

import inspect, os


class Theme:
    current_directory = os.path.dirname(inspect.getfile(inspect.currentframe()))

    @classmethod
    def getTheme(cls):
        return cls.setDark() if isDarkTheme() else cls.setLight()

    @classmethod
    def setDark(cls):
        dark_theme = cls.__read("dark")
        return dark_theme

    @classmethod
    def setLight(cls):
        light_theme = cls.__read("light")
        return light_theme

    @classmethod
    def __read(cls, mode):
        with open(
            os.path.join(cls.current_directory, f"{mode}\\theme.qss"), encoding="utf-8"
        ) as theme:
            return theme.read()
