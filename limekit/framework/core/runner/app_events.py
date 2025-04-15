"""
Observers; attachment to error message, engine destroy, print message callbacks,
"""

import sys


# Called by Limer to run an app. The following events can be subscribed to
class AppEvents:
    # All errors in the app
    errors_callback_listener = None

    # Notify that the engine has been destroyed from an error
    engine_destroy_callback_listener = None

    # Replace the print inbuilt-method with a custom one
    engine_print_callback_listerner = None

    # Listen to all errors in the app
    def subscribe_errors_listener(self, errors_callback_listener):
        self.errors_callback_listener = errors_callback_listener

    # Listen to engine destroy event
    def subscribe_engine_destroy_listener(self, engine_destroy_callback_listener):
        self.engine_destroy_callback_listener = engine_destroy_callback_listener

    # Listen to engine print event; anything that is printed in the app will be sent to this callback
    def subscribe_print_listener(self, engine_print_callback_listerner):
        self.engine_print_callback_listerner = engine_print_callback_listerner

    # Destroy the lua engine
    def destroy_engine(self):
        if self.engine_destroy_callback_listener:
            self.engine_destroy_callback_listener()

        sys.exit()

    def log_error_or_pass_callback(self, error):
        if self.errors_callback_listener:
            self.errors_callback_listener(error)
        else:
            print(error)

    def app_print(self, string):
        if self.engine_print_callback_listerner:
            self.engine_print_callback_listerner(string)
        else:
            print(string)
