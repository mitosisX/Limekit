from limekit.framework.core.engine.app_engine import EnginePart


class Converter(EnginePart):
    name = "__converters"

    @classmethod
    def convert_bytes(cls, size_bytes):
        # Define the suffixes for file sizes
        suffixes = ["B", "KB", "MB", "GB", "TB"]

        # Determine the appropriate suffix and perform the conversion
        for suffix in suffixes:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {suffix}"
            size_bytes /= 1024.0

        return f"{size_bytes:.2f} {suffixes[-1]}"  # If the file size is very large
