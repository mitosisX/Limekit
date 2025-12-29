"""
Limekit Error Handler
Centralized error handling and logging for the Limekit framework.
"""

import sys
import logging
import traceback
from datetime import datetime
from typing import Optional, Callable
from PySide6.QtWidgets import QMessageBox, QApplication


class LimekitErrorHandler:
    """Centralized error handler for Limekit framework."""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if LimekitErrorHandler._initialized:
            return

        self.logger = logging.getLogger("limekit")
        self._setup_logging()
        self._error_callbacks = []
        self._last_error = None
        self._error_count = 0

        LimekitErrorHandler._initialized = True

    def _setup_logging(self):
        """Configure logging with console and file handlers."""
        self.logger.setLevel(logging.DEBUG)

        # Console handler - show warnings and above
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        console_format = logging.Formatter(
            "%(levelname)s: %(message)s"
        )
        console_handler.setFormatter(console_format)

        # Detailed format for debugging
        detailed_format = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(module)s (%(filename)s:%(lineno)d): %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Only add handlers if not already added
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)

    def add_error_callback(self, callback: Callable):
        """Add a callback to be called when errors occur."""
        self._error_callbacks.append(callback)

    def handle_exception(
        self,
        exception: Exception,
        context: str = "",
        show_dialog: bool = False,
        fatal: bool = False
    ) -> None:
        """
        Handle an exception with proper logging and optional user notification.

        Args:
            exception: The exception that occurred
            context: Description of what was happening when error occurred
            show_dialog: Whether to show an error dialog to the user
            fatal: Whether this error should terminate the application
        """
        self._error_count += 1
        self._last_error = exception

        # Build error message
        error_type = type(exception).__name__
        error_msg = str(exception)
        tb = traceback.format_exc()

        if context:
            full_message = f"{context}: {error_type}: {error_msg}"
        else:
            full_message = f"{error_type}: {error_msg}"

        # Log the error
        self.logger.error(full_message)
        self.logger.debug(f"Traceback:\n{tb}")

        # Print to console for visibility
        print(f"\n{'='*60}")
        print(f"ERROR: {full_message}")
        if context:
            print(f"Context: {context}")
        print(f"{'='*60}")
        print(tb)

        # Notify callbacks
        for callback in self._error_callbacks:
            try:
                callback(exception, context)
            except Exception:
                pass  # Don't let callback errors cause more problems

        # Show dialog if requested
        if show_dialog:
            self._show_error_dialog(full_message, tb)

        # Handle fatal errors
        if fatal:
            self._handle_fatal_error(full_message)

    def handle_lua_error(self, exception: Exception, script_context: str = "") -> None:
        """Handle Lua-related errors with special formatting."""
        error_str = str(exception)

        # Parse Lua error for better formatting
        if '"<python>"]' in error_str:
            # Extract line number from Lua error
            try:
                init_index = error_str.rfind('>"]')
                sub_str = error_str[init_index + 4:]
                formatted = f"Lua SyntaxError: Line {sub_str}"
            except Exception:
                formatted = f"Lua Error: {error_str}"
        else:
            formatted = f"Lua Error: {error_str}"

        context = f"Lua execution{f' in {script_context}' if script_context else ''}"
        self.handle_exception(exception, context=context)
        print(f"\n{formatted}")

    def handle_widget_callback_error(
        self,
        exception: Exception,
        widget_type: str,
        event_type: str
    ) -> None:
        """Handle errors from widget event callbacks."""
        context = f"{widget_type}.{event_type} callback"
        self.handle_exception(exception, context=context)

    def handle_import_error(self, module_name: str, exception: Exception) -> None:
        """Handle module import errors."""
        context = f"Importing module '{module_name}'"
        self.logger.warning(f"Failed to import {module_name}: {exception}")

    def handle_build_error(self, exception: Exception, stage: str = "") -> None:
        """Handle build process errors."""
        context = f"Build process{f' ({stage})' if stage else ''}"
        self.handle_exception(exception, context=context, show_dialog=True)

    def _show_error_dialog(self, message: str, details: str = "") -> None:
        """Show an error dialog to the user."""
        try:
            app = QApplication.instance()
            if app is None:
                return

            dialog = QMessageBox()
            dialog.setIcon(QMessageBox.Icon.Critical)
            dialog.setWindowTitle("Limekit Error")
            dialog.setText(message[:500])  # Truncate long messages
            if details:
                dialog.setDetailedText(details)
            dialog.exec()
        except Exception:
            # If dialog fails, at least print
            print(f"Error Dialog: {message}")

    def _handle_fatal_error(self, message: str) -> None:
        """Handle fatal errors that require application shutdown."""
        print(f"\nFATAL ERROR: {message}")
        print("Application will now exit.")

        try:
            from limekit.engine.lifecycle.shutdown import destroy_engine
            destroy_engine()
        except Exception:
            pass

        sys.exit(1)

    def warn(self, message: str, context: str = "") -> None:
        """Log a warning message."""
        if context:
            self.logger.warning(f"{context}: {message}")
        else:
            self.logger.warning(message)

    def info(self, message: str) -> None:
        """Log an info message."""
        self.logger.info(message)

    def debug(self, message: str) -> None:
        """Log a debug message."""
        self.logger.debug(message)

    @property
    def error_count(self) -> int:
        """Get the total number of errors that have occurred."""
        return self._error_count

    @property
    def last_error(self) -> Optional[Exception]:
        """Get the last error that occurred."""
        return self._last_error


# Global error handler instance
error_handler = LimekitErrorHandler()


# Convenience functions for direct import
def handle_exception(exception: Exception, context: str = "", show_dialog: bool = False, fatal: bool = False):
    """Handle an exception using the global error handler."""
    error_handler.handle_exception(exception, context, show_dialog, fatal)


def handle_widget_error(exception: Exception, widget_type: str, event_type: str):
    """Handle a widget callback error."""
    error_handler.handle_widget_callback_error(exception, widget_type, event_type)


def handle_lua_error(exception: Exception, script_context: str = ""):
    """Handle a Lua error."""
    error_handler.handle_lua_error(exception, script_context)


def warn(message: str, context: str = ""):
    """Log a warning."""
    error_handler.warn(message, context)
