import lupa
import importlib
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
    def method_kwargs(method, *the_kwags):
        return lupa.unpacks_lua_table(method, the_kwags)

    @staticmethod
    def getattr(py_obj):
        return lupa.as_attrgetter(py_obj)

    @staticmethod
    def getitem(py_obj):
        return lupa.as_itemgetter(py_obj)

    @staticmethod
    def table_to_list(table):
        return list(table.values())

    @staticmethod
    def table_to_dict(table):
        return dict(table.items())

    @staticmethod
    def str_format(string: str, *args):
        return string.format(*args)

    @staticmethod
    def import_module(module):
        try:
            return importlib.import_module(module)
        except ModuleNotFoundError as ex:
            print(f"PythonImportError: {ex}")
