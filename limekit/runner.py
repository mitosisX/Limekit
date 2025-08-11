import os
import sys
from lupa import lua54
from limekit.utils.path import Path
from limekit.engine.app_engine import Engine
from limekit.engine.lifecycle.shutdown import destroy_engine
from limekit.core.exceptions.routes import RouteException

"""
  _     _                _    _ _     _____                                            _    
 | |   (_)_ __ ___   ___| | _(_) |_  |  ___| __ __ _ _ __ ___   _____      _____  _ __| | __
 | |   | | '_ ` _ \ / _ \ |/ / | __| | |_ | '__/ _` | '_ ` _ \ / _ \ \ /\ / / _ \| '__| |/ /
 | |___| | | | | | |  __/   <| | |_  |  _|| | | (_| | | | | | |  __/\ V  V / (_) | |  |   < 
 |_____|_|_| |_| |_|\___|_|\_\_|\__| |_|  |_|  \__,_|_| |_| |_|\___| \_/\_/ \___/|_|  |_|\_\
                                                                                            
"""


class LimerApplication:
    def __init__(self):
        self.engine = Engine()  # Behold! The Engine -- where all the magic happens

    def _handle_python_error(self, exception) -> None:
        if isinstance(exception, TypeError) and "takes exactly one argument" in str(
            exception
        ):
            excep_msg = str(exception)
            end = excep_msg.index("()") + 2
            exce_ = excep_msg[:end]
            print(
                f"NativeMethodError: Use of 'syntactic sugar' on {exce_.replace('.',':')}. "
                f"Use {exce_} instead."
            )
        else:
            print(exception)

    def _handle_lua_syntax_error(self, exception) -> None:
        exception_str = str(exception)
        if '"<python>"]' in exception_str:
            init_index = exception_str.rfind('>"]')
            sub_str = exception_str[init_index + 4 :]
            print(f"SyntaxError: Line {sub_str}")
        else:
            print(exception_str)

    def _handle_key_error(self, exception) -> None:
        print(
            f"AccessError: Could not access {exception}. "
            "Possible solution: try using py.getattr(py_method, args...)"
        )

    # . is passed when running Limer, but when running user projects, the actual path is passed instead
    def _initialize_path(self, location_arg: str) -> None:
        dir_path = (
            os.path.abspath(location_arg) if location_arg == "." else location_arg
        )
        Path.project_path = dir_path

    def run(self) -> None:
        try:
            if len(sys.argv) == 1:
                self._initialize_path(".")

            elif len(sys.argv) > 1:
                self._initialize_path(sys.argv[1])

            self.engine.start()

        except lua54.LuaSyntaxError as e:
            self._handle_lua_syntax_error(e)

        except KeyError as e:
            self._handle_key_error(e)

        except (TypeError, AttributeError, RuntimeError, NameError) as e:
            self._handle_python_error(e)

        except (RouteException, lua54.LuaError) as e:
            print(e)

        except Exception as e:
            print(f"Unexpected error: {e}")

        except ModuleNotFoundError as e:
            print(e)

        except TypeError as e:
            print(e)

        finally:
            if self.engine is not None:
                # destroy_engine()
                pass


app = LimerApplication()
app.run()
