import lupa
from functools import cache
from limekit.framework.core.engine.parts import EnginePart
from limekit.framework.handle.scripts.swissknife.converters import Converter


class Python(EnginePart):
    name = "py"

    @classmethod
    def str_indexing(cls, input_data, index_spec):
        try:
            # Evaluate the index_spec to create a slice object
            result = eval(f"'{input_data}'{index_spec}")
            # Use the slice object to extract the desired portion
            return result
        except (TypeError, IndexError, SyntaxError) as ex:
            return ex

    @classmethod
    def str_split(cls, string, delimeter):
        return Converter.table_from(string.split(delimeter))

    @classmethod
    def kwargs(cls, method, *the_kwags):
        return lupa.unpacks_lua_table(method, the_kwags)

    @classmethod
    def py_getattr(cls, py_obj):
        return lupa.as_attrgetter(py_obj)

    @classmethod
    def py_getitem(cls, py_obj):
        return lupa.as_itemgetter(py_obj)
