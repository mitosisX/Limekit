"""Exception taxonomy for the Limekit kernel.

Replaces the per-exception-type ladder in the old runner with a hierarchy
that callers can dispatch on.
"""


class LimekitError(Exception):
    """Root of every error Limekit raises deliberately."""


class BridgeError(LimekitError):
    """A value could not be marshalled between Lua and Python."""


class RegistryError(LimekitError):
    """A class could not be registered, or a lookup failed."""


class ProjectError(LimekitError):
    """The project on disk is missing or malformed."""


class RouteError(LimekitError):
    """A route could not be resolved to a resource."""


class LuaError(LimekitError):
    """Lua raised, or failed to compile.

    Carries the originating source file and line so callers never have to
    parse them back out of a message string.
    """

    def __init__(self, message, *, source="<unknown>", line=None):
        self.source = source
        self.line = line
        location = f"{source}:{line}" if line is not None else source
        super().__init__(f"{location}: {message}")


class WidgetCallbackError(LimekitError):
    """A Lua handler attached to a widget event raised."""

    def __init__(self, message, *, widget, event):
        self.widget = widget
        self.event = event
        super().__init__(f"{widget}.{event}: {message}")
