"""Looking inside a running project: its widget tree, and its properties.

Code injection on its own has never been much use, and the reason is worth
stating plainly. A normal `main.lua` reads:

    local window = ui.Window {}
    local label  = ui.Label("hello")

Those are *locals*. A chunk injected later runs in its own scope and cannot
see them, so the obvious thing to want -- "set that label's text" -- has no
name to reach for. 1.x shipped injection anyway; this is why it felt inert.

The way out is to stop using names. Every widget has a position in the Qt
object tree, and that position is stable for as long as the widget lives.
Address widgets by path and Lua's scoping stops mattering: the tree is the
thing that makes injection worth having.

Nothing here is exposed to Lua. A project cannot switch this on for itself;
only a launcher can, by setting LIMEKIT_INSPECT before starting it.
"""

from PySide6.QtWidgets import QApplication, QWidget

from limekit.kernel.bridge.convert import to_lua
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import method

# What a property value may be without being flattened to a string. Anything
# else -- a QFont, a widget, a colour object -- is reported by repr, because
# the far end of this is JSON and a channel that guesses is worse than one
# that admits it does not know.
_PRIMITIVES = (str, bool, int, float)


def top_level_widgets():
    """The project's windows, in a stable order.

    affinity holds every window that has been shown -- it must, or Lua would
    collect them -- but it is a set, so it is sorted here to give path "1"
    the same meaning on two consecutive calls.
    """
    from limekit.kernel.affinity import _windows

    windows = [w for w in _windows if w is not None]
    if not windows:
        # A project that never called show() still has widgets; falling back
        # to Qt's own list means the tree is not simply empty in that case.
        windows = [w for w in QApplication.topLevelWidgets() if w.isVisible()]
    return sorted(windows, key=lambda w: (w.windowTitle(), id(w)))


def child_widgets(widget):
    """Direct child widgets, in creation order.

    `QObject.children()` also returns layouts, actions, timers and the like.
    Only widgets are addressable here, and filtering rather than indexing
    into children() keeps a path meaning the same thing whether or not the
    widget happens to own a layout.
    """
    return [c for c in widget.children() if isinstance(c, QWidget)]


def lime_name(widget):
    """The name Lua knows this widget by, or Qt's class name.

    A widget built through Limekit carries `__lime__` ("ui.Button"). One Qt
    made on its own behalf -- a scroll area's viewport, a tab bar -- does
    not, and saying so is more honest than pretending it is part of the
    project.
    """
    lime = getattr(type(widget), "__lime__", None)
    return lime or f"<{type(widget).__name__}>"


def label_for(widget):
    """A short human hint: the button's text, the window's title."""
    for accessor in ("windowTitle", "text", "title", "objectName"):
        method = getattr(widget, accessor, None)
        if method is None:
            continue
        try:
            value = method()
        except TypeError:
            continue
        if isinstance(value, str) and value.strip():
            return " ".join(value.split())[:60]
    return ""


def resolve(path):
    """The widget at a dotted 1-based path, or None.

    Returns None rather than raising for a path that no longer resolves: a
    tree read a second ago describes an application that has since been free
    to close a dialog, and a stale path is an ordinary event here.
    """
    parts = [p for p in str(path).split(".") if p]
    if not parts:
        return None

    try:
        indices = [int(p) for p in parts]
    except ValueError:
        return None
    if any(i < 1 for i in indices):
        return None

    windows = top_level_widgets()
    if indices[0] > len(windows):
        return None

    widget = windows[indices[0] - 1]
    for index in indices[1:]:
        children = child_widgets(widget)
        if index > len(children):
            return None
        widget = children[index - 1]
    return widget


def tree(max_depth=12):
    """The whole project as nested nodes.

    Depth-capped because Qt's own internals nest further than anything a
    project author put there, and an unbounded walk of a complex window is a
    lot of JSON for information nobody asked for.
    """
    def node(widget, path, depth):
        entry = {
            "path": path,
            "class": lime_name(widget),
            "label": label_for(widget),
            "visible": bool(widget.isVisible()),
            "children": [],
        }
        if depth < max_depth:
            for index, child in enumerate(child_widgets(widget), start=1):
                entry["children"].append(node(child, f"{path}.{index}", depth + 1))
        return entry

    return [node(w, str(i), 1) for i, w in enumerate(top_level_widgets(), start=1)]


def _as_option_name(prop, raw):
    """Run an enum coercion backwards, so a value reads as its own name.

    A getter hands back Qt's enum member. Shown as-is that is
    "<Orientation.Vertical: 2>", which is neither what the author wrote nor
    anything they could write back.
    """
    mapping = getattr(prop.coerce, "mapping", None)
    if not mapping or isinstance(raw, _PRIMITIVES):
        return raw
    for name, member in mapping.items():
        if member == raw:
            return name
    return raw


def _readable(value):
    """A value the far end can render, and a note on what it really was."""
    if isinstance(value, bool):
        return value, "boolean"
    if isinstance(value, _PRIMITIVES):
        return value, type(value).__name__
    if value is None:
        return None, "nil"
    return repr(value), "object"


def properties(widget):
    """Every declared property of `widget`, read.

    Walks `__props__` rather than a hand-written list, so a widget that
    gains a property gains it here too. Props whose Qt accessor was never
    installed -- an abstract mixin's, on a class that does not combine with
    a matching Qt base -- are skipped, because reading them would raise.
    """
    out = []
    seen = set()

    for cls in type(widget).__mro__:
        for prop in getattr(cls, "__props__", ()):
            if prop.name in seen:
                continue

            getter, setter, _ = prop.accessor_names()
            if not hasattr(widget, getter):
                continue
            seen.add(prop.name)

            try:
                raw = getattr(widget, getter)()
            except Exception as exc:                  # a getter Qt refuses
                out.append({
                    "name": prop.name, "value": f"<unreadable: {exc}>",
                    "type": "error", "settable": False, "options": None,
                })
                continue

            options = getattr(prop.coerce, "options", None)
            raw = _as_option_name(prop, raw)
            value, kind = _readable(raw)
            out.append({
                "name": prop.name,
                "value": value,
                "type": kind,
                # Only the kinds that survive a JSON round trip can be sent
                # back. An object-typed property is shown, never edited.
                "settable": hasattr(widget, setter) and kind != "object",
                "options": sorted(options) if options else None,
                "setter": setter,
            })

    return sorted(out, key=lambda p: p["name"])


def set_property(widget, name, value):
    """Set one declared property, returning what it reads back as."""
    for cls in type(widget).__mro__:
        for prop in getattr(cls, "__props__", ()):
            if prop.name != name:
                continue

            getter, setter, _ = prop.accessor_names()
            if not hasattr(widget, setter):
                raise AttributeError(f"{name} cannot be set on this widget")

            getattr(widget, setter)(value)
            # Read back rather than echoing: coercion may have changed it,
            # and what the widget now holds is the only honest answer.
            return _readable(_as_option_name(prop, getattr(widget, getter)()))[0]

    raise AttributeError(f"no property named {name!r} on {lime_name(widget)}")


class Introspect(LimeObject):
    """The same reading, offered to Lua directly: `sys.Introspect`.

    The inspector reaches a *running* project over a socket. A designer
    building widgets in its own process needs the identical questions
    answered about objects it already holds, and going out through a socket
    to ask about something in the same address space would be absurd.

    So the walking and reading live in this module, and both callers use
    them: `services/inspector.py` over the wire, this class in process.
    """

    __lime__ = "sys.Introspect"

    @staticmethod
    @method({"widget": "any"}, returns="table[]",
            doc="Every declared property of a widget: name, value, type, "
                "options and whether it can be set.")
    def properties(widget):
        return to_lua(properties(widget))

    @staticmethod
    @method({"widget": "any", "name": "string"}, returns="any",
            doc="One property's current value.")
    def getProperty(widget, name):
        for entry in properties(widget):
            if entry["name"] == name:
                return entry["value"]
        raise BridgeError(f"no property named {name!r} on {lime_name(widget)}")

    @staticmethod
    @method({"widget": "any", "name": "string", "value": "any"}, returns="any",
            doc="Sets one property, returning what it reads back as.")
    def setProperty(widget, name, value):
        return set_property(widget, name, value)

    @staticmethod
    @method({"widget": "any"}, returns="string",
            doc="The name Lua knows a widget by, such as ui.Button.")
    def className(widget):
        return lime_name(widget)

    @staticmethod
    @method(returns="string[]",
            doc="Every widget class that can be built with no arguments.")
    def buildableClasses():
        """What a palette can offer.

        A designer has to be able to make one of whatever it lists, and
        three classes -- GifPlayer, KeyboardShortcut, Spacer -- cannot be
        made without being told something first. Listing them anyway would
        put items in a palette that fail when dropped.
        """
        from limekit.kernel import introspect as reflection
        from limekit.kernel.registry import registry

        names = []
        for name, cls in registry.modules().get("ui", {}).items():
            ctor = reflection.constructor(cls)
            if ctor is None or any(not has_default for _, _, has_default in ctor.params):
                continue
            names.append(name)
        return to_lua(sorted(names))
