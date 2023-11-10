import sys
from lupa import lua54
from limekit.framework.core.engine.app_engine import Engine
from limekit.framework.core.exceptions.routes import RouteException


class AppRun:
    errors_callback_listener = None  # A
    engine_destroy_callback_listener = None  # A

    def subscribe_errors_listener(self, errors_callback_listener):
        self.errors_callback_listener = errors_callback_listener

    def subscribe_engine_destroy_listener(self, engine_destroy_callback_listener):
        self.engine_destroy_callback_listener = engine_destroy_callback_listener

    def destroy_engine(self):
        if self.engine_destroy_callback_listener:
            self.engine_destroy_callback_listener()
        else:
            sys.exit()

    def log_error_or_pass_callback(self, error):
        if self.errors_callback_listener:
            self.errors_callback_listener(error)
        else:
            print(error)

    def run(self):
        try:
            engine = Engine()
            engine.start()
        except TypeError as exception:
            excep_msg = str(exception)

            if "takes exactly one argument" in excep_msg:
                end = excep_msg.index("()") + 2

                exce_ = str(excep_msg)[:end]
                self.log_error_or_pass_callback(
                    f"NativeMethodError: Use of 'syntactic sugar' on {exce_.replace('.',':')}. Use {exce_} instead."
                )
            else:
                self.log_error_or_pass_callback(exception)

            self.destroy_engine()

        except lua54.LuaSyntaxError as ex:
            # self.log_error_or_pass_callback(exception)

            exception = str(ex)

            if "unexpected symbol near" in exception:
                init_index = exception.rfind('>"]')
                sub_str = exception[init_index + 4 :]

                # right_index = sub_str.rfind(": ")
                # final_str = sub_str[:right_index]
                # symbol_index = exception.find("near ")

                self.log_error_or_pass_callback(f"SyntaxError: Line {sub_str}")
                # self.log_error_or_pass_callback(final_str)

            self.destroy_engine()

        except lua54.LuaError as exception:
            self.log_error_or_pass_callback(exception)

            self.destroy_engine()

        except RouteException as exception:
            self.log_error_or_pass_callback(exception)

            self.destroy_engine()

        except AttributeError as exception:
            self.log_error_or_pass_callback(exception)

            self.destroy_engine()

        except KeyError as exception:
            self.log_error_or_pass_callback(
                f"AccessError: Could not access {exception}. Possible way, try using: py.getattr(py_method, args...)"
            )

            self.destroy_engine()

        except RuntimeError as exception:
            self.log_error_or_pass_callback(exception)

            self.destroy_engine()
