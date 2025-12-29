"""
Limekit Application Runner
Entry point for running Limekit applications.
"""

import os
import sys
import traceback
from lupa import lua54
from limekit.utils.path import Path
from limekit.engine.app_engine import Engine
from limekit.engine.lifecycle.shutdown import destroy_engine
from limekit.core.exceptions.routes import RouteException
from limekit.core.error_handler import error_handler, handle_exception, handle_lua_error


class LimerApplication:
    def __init__(self):
        self.engine = None

    def _initialize_engine(self):
        """Initialize the Limekit engine."""
        self.engine = Engine()

    def _initialize_path(self, location_arg: str) -> None:
        """Set up the project path."""
        dir_path = (
            os.path.abspath(location_arg) if location_arg == "." else location_arg
        )
        Path.project_path = dir_path

    def _format_python_error(self, exception: Exception) -> str:
        """Format Python errors with helpful messages."""
        error_str = str(exception)

        if isinstance(exception, TypeError) and "takes exactly one argument" in error_str:
            try:
                end = error_str.index("()") + 2
                method_name = error_str[:end]
                return (
                    f"NativeMethodError: Incorrect use of colon syntax on '{method_name}'.\n"
                    f"  Hint: Use {method_name.replace('.', ':')} with dot notation instead,\n"
                    f"  or check if you're passing the correct number of arguments."
                )
            except ValueError:
                pass

        if isinstance(exception, AttributeError):
            return f"AttributeError: {error_str}\n  Hint: Check if the method/property exists on this object."

        if isinstance(exception, NameError):
            return f"NameError: {error_str}\n  Hint: Make sure the variable or function is defined before use."

        return str(exception)

    def _format_lua_error(self, exception: Exception) -> str:
        """Format Lua errors with line numbers."""
        error_str = str(exception)

        if '"<python>"]' in error_str:
            try:
                init_index = error_str.rfind('>"]')
                line_info = error_str[init_index + 4:]
                return f"Lua SyntaxError: Line {line_info}"
            except Exception:
                pass

        return f"Lua Error: {error_str}"

    def _format_key_error(self, exception: Exception) -> str:
        """Format key access errors."""
        return (
            f"AccessError: Could not access {exception}.\n"
            f"  Hint: Try using py.getattr(object, 'attribute') for Python object access."
        )

    def run(self) -> None:
        """Run the Limekit application."""
        exit_code = 0

        try:
            # Initialize path from command line argument
            if len(sys.argv) > 1:
                self._initialize_path(sys.argv[1])

            # Initialize and start the engine
            self._initialize_engine()
            self.engine.start()

        except lua54.LuaSyntaxError as e:
            error_msg = self._format_lua_error(e)
            print(f"\n{error_msg}")
            handle_lua_error(e)
            exit_code = 1

        except lua54.LuaError as e:
            error_msg = self._format_lua_error(e)
            print(f"\n{error_msg}")
            handle_lua_error(e)
            exit_code = 1

        except KeyError as e:
            error_msg = self._format_key_error(e)
            print(f"\n{error_msg}")
            handle_exception(e, context="Key access")
            exit_code = 1

        except TypeError as e:
            error_msg = self._format_python_error(e)
            print(f"\nTypeError: {error_msg}")
            handle_exception(e, context="Type error")
            exit_code = 1

        except AttributeError as e:
            error_msg = self._format_python_error(e)
            print(f"\n{error_msg}")
            handle_exception(e, context="Attribute access")
            exit_code = 1

        except NameError as e:
            error_msg = self._format_python_error(e)
            print(f"\n{error_msg}")
            handle_exception(e, context="Name resolution")
            exit_code = 1

        except RuntimeError as e:
            print(f"\nRuntimeError: {e}")
            handle_exception(e, context="Runtime")
            exit_code = 1

        except RouteException as e:
            print(f"\nRouteError: {e}")
            handle_exception(e, context="Routing")
            exit_code = 1

        except ModuleNotFoundError as e:
            print(f"\nModuleNotFoundError: {e}")
            print("  Hint: Make sure all required packages are installed.")
            handle_exception(e, context="Module import")
            exit_code = 1

        except FileNotFoundError as e:
            print(f"\nFileNotFoundError: {e}")
            print("  Hint: Check if the file path is correct.")
            handle_exception(e, context="File access")
            exit_code = 1

        except Exception as e:
            # Catch-all for unexpected errors
            print(f"\n{'='*60}")
            print(f"Unexpected Error: {type(e).__name__}: {e}")
            print(f"{'='*60}")
            traceback.print_exc()
            handle_exception(e, context="Unexpected error")
            exit_code = 1

        finally:
            # Always attempt cleanup
            if self.engine is not None:
                try:
                    destroy_engine()
                except Exception as cleanup_error:
                    error_handler.warn(f"Cleanup error: {cleanup_error}")

        if exit_code != 0:
            sys.exit(exit_code)


# Application entry point
app = LimerApplication()
app.run()
