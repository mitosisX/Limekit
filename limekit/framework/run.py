# Yeah, I know... This looks half done. But hey, it's working right?
import sys
from lupa import lua54
from limekit.framework.core.engine.app_engine import Engine
from limekit.framework.core.exceptions.routes import RouteException

# print(os.getcwd())


def destroy_engine():
    sys.exit()


try:
    engine = Engine()
    engine.start()
except TypeError as exception:
    excep_msg = str(exception)

    if "takes exactly one argument" in excep_msg:
        end = excep_msg.index("()") + 2

        exce_ = str(excep_msg)[:end]
        print(
            f"NativeMethodError: Use of 'syntactic sugar' on {exce_.replace('.',':')}. Use {exce_} instead."
        )
    else:
        print(exception)

    destroy_engine()


except lua54.LuaSyntaxError as ex:
    # print(exception)

    exception = str(ex)

    if "unexpected symbol near" in exception:
        init_index = exception.rfind('>"]')
        sub_str = exception[init_index + 4 :]

        # right_index = sub_str.rfind(": ")
        # final_str = sub_str[:right_index]
        # symbol_index = exception.find("near ")

        print(f"SyntaxError: Line {sub_str}")
        # print(final_str)

    destroy_engine()

except lua54.LuaError as exception:
    print(exception)

    destroy_engine()

except RouteException as exception:
    print(exception)

    destroy_engine()

except AttributeError as exception:
    print(exception)

    destroy_engine()

except KeyError as exception:
    print(
        f"AccessError: Could not access {exception}. Possible way, try using: py.getattr(py_method, args...)"
    )

    destroy_engine()

except RuntimeError as exception:
    print(exception)

    destroy_engine()
