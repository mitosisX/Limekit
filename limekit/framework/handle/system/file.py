import os
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.handle.paths.path import Path


class File(EnginePart):
    name = "__file"

    @classmethod
    def remove_file(cls, file):
        if Path.check_path(file):
            os.remove(file)

    # Removing self to allow direct access to the methods
    @staticmethod
    def read_file(file, encoding="utf-8"):
        with open(file, "r", encoding=encoding) as file:
            return file.read()

    @classmethod
    def script_file_reader(cls, file, encoding):
        if "::" in file:  # and (not "\\" in file and not "//" in file):
            # print("here")
            file_path = Path.process_route_makers(file)
            return cls.read_file(file_path)

        return cls.read_file(file, encoding)

    @classmethod
    def create_file(cls, file):
        cls.write_file(file, "")

    @staticmethod
    def write_file(file, content, encoding="utf-8"):
        with open(file, "w", encoding=encoding) as file:
            file.write(content)

    @staticmethod
    def append_file(file, content, encoding="utf-8"):
        with open(file, "a", encoding=encoding) as file:
            file.write(content)

    @staticmethod
    def write_bytes(file, bytes):
        with open(file, "wb") as file:
            file.write(bytes)
