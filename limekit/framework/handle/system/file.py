from limekit.framework.core.engine.parts import EnginePart


class File(EnginePart):
    name = "__file"

    # Removing self to allow direct access to the methods
    def read_file(file, encoding="utf-8"):
        with open(file, "r", encoding=encoding) as file:
            return file.read()

    def write_file(file, content, encoding="utf-8"):
        with open(file, "w", encoding=encoding) as file:
            file.write(content)

    def append_file(file, content, encoding="utf-8"):
        with open(file, "a", content=content) as file:
            file.write(content)

    def write_bytes(file, bytes):
        with open(file, "wb") as file:
            file.write(bytes)
