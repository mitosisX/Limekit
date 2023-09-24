from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.handle.paths.path import Path


class File(EnginePart):
    name = "__file"

    # Removing self to allow direct access to the methods
    @classmethod
    def read_file(cls, file, encoding="utf-8"):
        with open(file, "r", encoding=encoding) as file:
            return file.read()

    @classmethod
    def script_file_reader(cls, file, encoding):
        if ":" in file and not "\\" in file and not "//" in file:
            file = Path.process_route_makers(file)

        return cls.read_file(file, encoding)

    @classmethod
    def write_file(cls, file, content, encoding="utf-8"):
        with open(file, "w", encoding=encoding) as file:
            file.write(content)

    @classmethod
    def append_file(cls, file, content, encoding="utf-8"):
        with open(file, "a", content=content) as file:
            file.write(content)

    @classmethod
    def write_bytes(cls, file, bytes):
        with open(file, "wb") as file:
            file.write(bytes)
