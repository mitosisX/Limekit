# Yeah, I know... This looks half done. But hey, it's working right?
import os
import sys
from lupa import lua54
from limekit.framework.handle.paths.path import Path
from limekit.framework.core.engine.app_engine import Engine
from limekit.framework.core.engine.destroyer import destroy_engine
from limekit.framework.core.exceptions.routes import RouteException

"""
  _     _                _    _ _     _____                                            _    
 | |   (_)_ __ ___   ___| | _(_) |_  |  ___| __ __ _ _ __ ___   _____      _____  _ __| | __
 | |   | | '_ ` _ \ / _ \ |/ / | __| | |_ | '__/ _` | '_ ` _ \ / _ \ \ /\ / / _ \| '__| |/ /
 | |___| | | | | | |  __/   <| | |_  |  _|| | | (_| | | | | | |  __/\ V  V / (_) | |  |   < 
 |_____|_|_| |_| |_|\___|_|\_\_|\__| |_|  |_|  \__,_|_| |_| |_|\___| \_/\_/ \___/|_|  |_|\_\
                                                                                            
"""

# This is where the exception handling happens

try:
    if len(sys.argv) > 1:
        location_arg = sys.argv[1]

        # . is passed when running Limer, but the actual path is passed when running user projects
        dir_path = (
            os.path.abspath(location_arg) if location_arg == "." else location_arg
        )
        Path.project_path = dir_path

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
        #
        #                   !!!!!!!!!!!!!!!!!!!!!!!!!!
        #   This is where most of the python related errors are handled
        #
        print(exception)

    destroy_engine()


except lua54.LuaSyntaxError as ex:
    # print(exception)

    exception = str(ex)

    if '"<python>"]' in exception:
        init_index = exception.rfind('>"]')
        sub_str = exception[init_index + 4 :]

        # right_index = sub_str.rfind(": ")
        # final_str = sub_str[:right_index]
        # symbol_index = exception.find("near ")

        print(f"SyntaxError: Line {sub_str}")
        # print(final_str)

    else:
        # print("here")
        print(ex)
        pass

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

except NameError as exception:
    print(exception)
    destroy_engine()
