from limekit.framework.core.engine.parts import EnginePart
import hashlib


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
    def py_kwargs_(cls, *args):
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

    # redesign of the above method. Just remebered about unboxing, so had to shorten it.
    # 14 September, 2023 (4:57 PM) (Thursday) (Mzuzu)
    # @classmethod
    def py_kwargs(*args_):
        # Custom designed method that allows passing of *ags and **kwargs to any python method

        # NOTE: if an error occurs of _LuaTable.. json().. what what, user should just convert their lua table to dict()

        py_method, *args, kwargs = args_
        kwargs = dict(kwargs)
        try:
            if args:
                ret_method_args = py_method(*args, **kwargs)
                return ret_method_args
            else:
                ret_method_kwargs = py_method(**kwargs)
                return ret_method_kwargs
        except TypeError as ex:
            # py_method(*[None], **kwargs)
            print(ex)

    # Allows using python indexing [:], [::2], [::-1]
    @classmethod
    def py_indexing(cls, input_data, index_spec):
        try:
            # Evaluate the index_spec to create a slice object
            result = eval(f"""{input_data}{index_spec}""")
            # Use the slice object to extract the desired portion
            return result
        except (TypeError, IndexError, SyntaxError) as ex:
            return ex

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

    # available hashes: md5, sha1, sha224, sha256, sha384, sha512, sha3_224, sha3_256, sha3_384, sha3_512
    @classmethod
    def make_hash_string(cls, hash_type, text: str):
        try:
            h = hashlib.new(hash_type)
            h.update(text.encode("utf-8"))
            return h.hexdigest()
        except ValueError as exception:
            print(exception)

    @classmethod
    def string_split(cls, string, delimeter):
        return list(string.split(delimeter))

    # redefining some of the in-built python methods

    """
            Using zip() method in lua
            
    names = {'John', 'Mary', 'Martha', 'James'}
    grades = {10, 80, 100, 56}
    col = zip(names, grades)
    output: [('John', 10), ('Mary', 80), ('Martha', 100), ('James', 56)]
    
    and when one passes to dict(), it returns {'John': 10, 'Mary': 80, 'Martha': 100, 'James': 56}
    """

    # The crazy thing about list() is that, when you use it on lua table, and try to access the
    # elements in lua is that, the indexing starts at 0, same as python. Python's indexing takes dominance
    # over lua's indexing (which starts at 1)
    @classmethod
    def list_(cls, list_items):
        ret_list = []
        for a in range(len(list_items)):
            ret_list.append(list_items[a + 1])  # + 1 coz lua indexes at 1

        return ret_list

    @classmethod
    def zip_(cls, arg1, arg2):
        return list(zip(cls.list_(arg1), cls.list_(arg2)))
