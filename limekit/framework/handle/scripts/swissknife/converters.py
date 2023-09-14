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

    @classmethod
    def py_kwargs_old(cls, *args):
        # kwargs = {key: value for key, value in data.items() if key != "location"}
        py_method = args[0]  # the first is always the target py method
        kwargs = dict(args[-1])  # the last bit should be a lua table
        args = [arg for arg in args[1:-1]]  # anything in between are arguments

        if args:
            try:
                return py_method(*args, **kwargs)
            except TypeError as ex:
                print(ex)
        else:
            try:
                return py_method(**kwargs)
            except TypeError as ex:
                # py_method(*[None], **kwargs)
                print(ex)

    # redesign of the above method. Just remebered about unboxing and to shorten it.
    # 14 September, 2023 (4:57 PM) (Thursday) (Mzuzu)
    @classmethod
    def py_kwargs(cls, *args_):
        # Custom designed method that allows passing of *ags and **kwargs to any python method
        py_method, *args, kwargs = args_
        try:
            if args:
                return py_method(*args, **kwargs)
            else:
                return py_method(**kwargs)
        except TypeError as ex:
            # py_method(*[None], **kwargs)
            print(ex)

    @classmethod
    def test(cls, location, name="", age=None):
        if location:
            print(location)
        if name:
            print(name)
        if age:
            print(age)

    @classmethod
    def hex_to_rgb(cls, hex):
        hex = hex.lstrip("#")
        hlen = len(hex)

        return list(int(hex[i : i + hlen // 3], 16) for i in range(0, hlen, hlen // 3))
