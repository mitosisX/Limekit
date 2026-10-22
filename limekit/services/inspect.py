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


def _is_limekit(widget):
    return getattr(type(widget), "__lime__", None) is not None


def child_widgets(widget):
    """The Limekit widgets directly inside `widget`, in creation order.

    `QObject.children()` also returns layouts, actions, timers and the like.
    It returns the parts Qt builds for itself too -- a spinner's text box, a
    list's viewport and scroll bars, a tab's bar -- and those are nobody's
    project. They are looked through, not listed: a label inside a
    scroller's viewport is the scroller's child here, as it is in the Lua
    that put it there. Paths count only what this returns, so a path means
    the same thing whatever Qt has made around a widget.
    """
    found = []
    for child in widget.children():
        if not isinstance(child, QWidget):
            continue
        if _is_limekit(child):
            found.append(child)
        else:
            found.extend(child_widgets(child))
    return found


# Where several Limekit classes share a Qt base, the one a widget of that
# base most plausibly is.
_PREFERRED = {"QLabel": "ui.Label", "QFrame": "ui.Container", "QWidget": "ui.Container"}


def _name_by_base():
    """Qt base class name -> the Limekit class built on it, where only one is."""
    from limekit.kernel.registry import registry

    seen = {}
    for path in registry.paths():
        if not path.startswith("ui."):
            continue
        for base in registry.get(path).__bases__:
            if base.__module__.startswith("PySide6"):
                seen.setdefault(base.__name__, set()).add(path)
    names = {qt: paths.pop() for qt, paths in seen.items() if len(paths) == 1}
    names.update(_PREFERRED)
    return names


def lime_name(widget):
    """The name Lua knows this widget by: "ui.Button".

    A widget Limekit did not build -- a dialog Qt raised, a top-level window
    found by Qt's own list -- is named after the Limekit class it most
    resembles. A Qt class name never reaches the person looking.
    """
    lime = getattr(type(widget), "__lime__", None)
    if lime:
        return lime
    names = _name_by_base()
    for cls in type(widget).__mro__:
        if cls.__name__ in names:
            return names[cls.__name__]
    return "ui.Container"


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


def describe(value):
    """A value that is not a string, number or boolean, put in words.

    repr() would say "<PySide6.QtGui.QIcon(null) at 0x...>": Qt's name for
    it and an address, neither of which means anything to a Lua author.
    """
    from PySide6.QtCore import QSize
    from PySide6.QtGui import QFont, QIcon, QImage, QKeySequence, QPixmap

    if isinstance(value, QWidget):
        return f"{lime_name(value)} {label_for(value)}".strip()
    if isinstance(value, QIcon):
        return "no icon" if value.isNull() else "icon"
    if isinstance(value, (QPixmap, QImage)):
        return "no image" if value.isNull() else f"image {value.width()} x {value.height()}"
    if isinstance(value, QFont):
        return f"{value.family()}, {value.pointSize()} pt"
    if isinstance(value, QSize):
        return f"{value.width()} x {value.height()}"
    if isinstance(value, QKeySequence):
        return value.toString() or "none"
    if isinstance(value, (list, tuple)):
        return ", ".join(str(v) if isinstance(v, _PRIMITIVES) else describe(v)
                         for v in value) or "empty"
    if hasattr(value, "name") and hasattr(type(value), "__members__"):
        return str(value.name).lower()               # an enum member
    try:
        from limekit.kernel.bridge.engine import lupa
        kind = lupa.lua_type(value)                       # a Lua table or function
    except Exception:
        kind = None
    return kind or getattr(type(value), "__lime__", None) or "a value"


def _readable(value):
    """A value the far end can render, and a note on what it really was."""
    if isinstance(value, bool):
        return value, "boolean"
    if isinstance(value, _PRIMITIVES):
        return value, type(value).__name__
    if value is None:
        return None, "nil"
    return describe(value), "object"


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


def buildable_classes():
    """Bare names ("Button") of every ui class constructible with no
    arguments, sorted. The palette and `Introspect.buildableClasses` both
    read this, so they cannot disagree."""
    from limekit.kernel import introspect as reflection
    from limekit.kernel.registry import registry

    names = []
    for name, cls in registry.modules().get("ui", {}).items():
        ctor = reflection.constructor(cls)
        # No __init__ of Limekit's own means Qt's, which takes no arguments:
        # ui.Spinner() builds. Counting that as "not buildable" kept Spinner,
        # DoubleSpinner and ProgressBar off the designer's palette.
        if ctor is not None and any(not has_default for _, _, has_default in ctor.params):
            continue
        names.append(name)
    return sorted(names)


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
        return to_lua(buildable_classes())
