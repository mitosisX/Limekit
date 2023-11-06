import lupa
from functools import cache
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.handle.scripts.swissknife.converters import Converter


class Python(EnginePart):
    name = "py"

    @staticmethod
    def str_indexing(input_data, index_spec):
        try:
            # Evaluate the index_spec to create a slice object
            result = eval(f"'{input_data}'{index_spec}")
            # Use the slice object to extract the desired portion
            return result
        except (TypeError, IndexError, SyntaxError) as ex:
            return ex

    @staticmethod
    def str_split(string, delimeter=","):
        return Converter.table_from(string.split(delimeter))

    @staticmethod
    def kwargs(method, *the_kwags):
        return lupa.unpacks_lua_table(method, the_kwags)

    @staticmethod
    def getattr(py_obj):
        return lupa.as_attrgetter(py_obj)

    @staticmethod
    def getitem(py_obj):
        return lupa.as_itemgetter(py_obj)

    @staticmethod
    def table2list(table):
        return list(table.values())

    @staticmethod
    def int_range(start, end):
        return Converter.table_from(list(range(start, end)))

    @staticmethod
    def str_format(string: str, *args):
        return string.format(*args)
