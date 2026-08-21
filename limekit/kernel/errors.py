"""Exception taxonomy for the Limekit kernel.

Replaces the per-exception-type ladder in the old runner with a hierarchy
that callers can dispatch on.
"""

import re


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


# Lua reports errors as [string "name"]:LINE: message, optionally followed
# by its own "stack traceback:" section. Runtime errors start with the
# location directly; compile errors are prefixed with "error loading code: ",
# so this must SEARCH the text rather than anchor to its start.
_LUA_LOCATION = re.compile(
    r'\[string "(?P<source>[^"]*)"\]:(?P<line>\d+):\s*(?P<message>.*)',
    re.DOTALL,
)


def parse_lua_error(text, *, fallback_source="<limekit>"):
    """Split a raw lupa error string into its parts.

    lupa hands back one string with the location, the message and Lua's own
    stack traceback run together, and every caller wants them apart: the
    location to point at, the message to show a person, and the traceback
    only when someone asks for it. Reporting the lot as one blob is how a
    one-line mistake ends up filling a console.

    Returns (message, source, line, traceback), where line is None and
    source is `fallback_source` if the text carries no location.
    """
    body, trace = text, ""

    marker = body.find("stack traceback:")
    if marker != -1:
        trace = body[marker:].strip()
        body = body[:marker].rstrip()

    match = _LUA_LOCATION.search(body)
    if match:
        lines = match.group("message").strip().splitlines()
        return (lines[0].strip() if lines else body.strip(),
                match.group("source") or fallback_source,
                int(match.group("line")),
                trace)

    lines = body.strip().splitlines()
    return (lines[0].strip() if lines else text.strip(), fallback_source, None, trace)


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
    """A Lua handler attached to a widget event raised.

    The message is one line naming the widget, the event, the file and the
    line -- everything needed to go and look. Lua's stack traceback is kept
    on `details` rather than folded into the message, because a console that
    prints the message is not asking for six lines of it, and the one thing
    a person needs was previously buried under them.
    """

    def __init__(self, message, *, widget, event, source=None, line=None,
                 details=""):
        self.widget = widget
        self.event = event
        self.source = source
        self.line = line
        self.details = details

        location = ""
        if source:
            location = f"{source}:{line}: " if line is not None else f"{source}: "

        super().__init__(f"{widget}.{event}: {location}{message}")

    @classmethod
    def from_exception(cls, exc, *, widget, event):
        """Build one from whatever a guarded callback threw.

        A Lua error arrives as a single lupa string with the location, the
        message and the traceback run together; anything else is a plain
        Python exception and has no Lua location to find.
        """
        message, source, line, details = parse_lua_error(str(exc))
        if line is None:
            source = None                  # not a Lua error; do not invent one
        return cls(message, widget=widget, event=event,
                   source=source, line=line, details=details)
