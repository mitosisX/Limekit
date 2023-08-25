from limekit.framework.core.engine.parts import EnginePart


class File(EnginePart):
    name = "__file"

    # Removing self to allow direct access to the methods
    def read_file(file):
        with open(file, "r") as file:
            return file.read()

    def write_file(file, content):
        with open(file, "w") as file:
            file.write(content)

    def append_file(file, content):
        with open(file, "a") as file:
            file.write(content)

    def create_file(file_):
        with open(file_, "w"):
            pass

    def write_bytes(file, bytes):
        with open(file, "wb") as file:
            file.write(bytes)
