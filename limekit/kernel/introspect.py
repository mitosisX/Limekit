"""Discovery of the hand-written surface, for the generators.

Prop and Event are declarations, so the generators can just read
`cls.__props__` and `cls.__events__`. Hand-written methods are not declared
anywhere -- which is exactly why the stubs used to omit `addChild`, `setData`,
`addSeries` and every other method-shaped API, leaving whole classes
(`BarChart`, `CategoryAxis`) documented as empty tables.

This module recovers them by inspection, and merges in any `@method`
enrichment it finds.

Nothing here runs at import time. Collecting signatures for ~80 classes is
slow enough to matter for a GUI app's startup, and only the three generators
in tools/ ever need it, so it stays a function they call rather than work
done in `LimeObject.__init_subclass__`.
"""

import ast
import inspect
import textwrap

# Qt virtual methods a widget overrides to *implement* itself. They are public
# by name but are not API -- no Lua caller invokes `paintEvent`; Qt does.
_QT_VIRTUALS = frozenset({
    "paintEvent", "keyPressEvent", "keyReleaseEvent", "mousePressEvent",
    "mouseReleaseEvent", "mouseMoveEvent", "mouseDoubleClickEvent",
    "wheelEvent", "showEvent", "hideEvent", "closeEvent", "resizeEvent",
    "contextMenuEvent", "focusInEvent", "focusOutEvent", "enterEvent",
    "leaveEvent", "dragEnterEvent", "dragMoveEvent", "dropEvent",
    "changeEvent", "moveEvent", "event", "eventFilter", "run",
})


class MethodInfo:
    """One hand-written method, as the generators need to see it."""

    def __init__(self, name, *, params, has_varargs, is_static, returns, doc,
                 declared_on):
        self.name = name
        self.params = params            # [(name, lua_type_or_None, has_default)]
        self.has_varargs = has_varargs
        self.is_static = is_static
        self.returns = returns          # a Lua type string, or None
        self.doc = doc
        self.declared_on = declared_on

    def __repr__(self):                                     # pragma: no cover
        return f"<MethodInfo {self.declared_on}.{self.name}>"


def _is_limekit_class(klass):
    return (getattr(klass, "__module__", "") or "").startswith("limekit.")


def _unwrap(raw):
    """Return (function, is_static) for a class-dict entry, or (None, False)."""
    if isinstance(raw, staticmethod):
        return raw.__func__, True
    if isinstance(raw, classmethod):
        return raw.__func__, False
    if inspect.isfunction(raw):
        return raw, False
    return None, False


def _returns_self(fn):
    """Whether the function has a `return self` -- i.e. whether it chains.

    Chaining is a headline 2.0 convention (`label:setText("Hi"):setWordWrap(true)`)
    and almost every hand-written setter ends in `return self`, but nothing
    records that anywhere a generator can read. Rather than decorate a few
    hundred methods by hand, read it off the AST: any `return self` counts.

    Source is not always available (a C extension, an exec'd definition), in
    which case we simply do not claim a return type.
    """
    try:
        source = textwrap.dedent(inspect.getsource(fn))
    except (OSError, TypeError):                            # pragma: no cover
        return False
    try:
        tree = ast.parse(source)
    except SyntaxError:                                     # pragma: no cover
        return False
    return any(
        isinstance(node, ast.Return)
        and isinstance(node.value, ast.Name)
        and node.value.id == "self"
        for node in ast.walk(tree)
    )


def _describe(name, fn, is_static, declared_on):
    spec = getattr(fn, "_lime_method", None)
    declared_types = spec.params if spec else {}

    try:
        signature = inspect.signature(fn)
    except (TypeError, ValueError):                         # pragma: no cover
        return None

    params, has_varargs = [], False
    for index, (pname, param) in enumerate(signature.parameters.items()):
        if index == 0 and not is_static and pname in ("self", "cls"):
            continue
        if param.kind is param.VAR_POSITIONAL:
            has_varargs = True
            continue
        if param.kind is param.VAR_KEYWORD:
            # Lua has no **kwargs. Constructors that take (self, /, *args,
            # **kwargs) are inherited Qt signatures carrying no real
            # information, so nothing is lost by dropping them.
            continue
        params.append((
            pname,
            declared_types.get(pname),
            param.default is not param.empty,
        ))

    # fn.__doc__, not inspect.getdoc: getdoc falls back to an inherited
    # docstring, which for an undocumented __init__ yields object.__init__'s
    # "Initialize self. See help(type(self))..." -- noise in every stub.
    doc = (spec.doc if spec and spec.doc else fn.__doc__) or ""

    returns = spec.returns if spec else None
    if returns is None and not is_static and _returns_self(fn):
        returns = "self"

    return MethodInfo(
        name,
        params=params,
        has_varargs=has_varargs,
        is_static=is_static,
        returns=returns,
        doc=doc.strip(),
        declared_on=declared_on,
    )


def public_methods(cls):
    """Hand-written public methods on `cls`, nearest ancestor winning.

    Excluded: anything private, the accessors `declarative` generated (they
    are tagged `_lime_generated` and already described by `__props__` /
    `__events__`), Qt virtuals, and everything defined outside `limekit.` --
    which is what keeps the several hundred inherited QWidget methods out.
    """
    found = {}
    for klass in cls.__mro__:
        if not _is_limekit_class(klass):
            continue
        for name, raw in vars(klass).items():
            if name.startswith("_") or name in found or name in _QT_VIRTUALS:
                continue
            fn, is_static = _unwrap(raw)
            if fn is None or getattr(fn, "_lime_generated", False):
                continue
            info = _describe(name, fn, is_static, klass.__name__)
            if info is not None:
                found[name] = info
    return tuple(sorted(found.values(), key=lambda m: m.name))


def constructor(cls):
    """The class's own `__init__` as a MethodInfo, or None if it has none.

    Used to document `ui.Button("Save")` and `ui.Window { title = ... }`,
    neither of which appeared in the stubs at all.
    """
    for klass in cls.__mro__:
        if not _is_limekit_class(klass):
            continue
        raw = vars(klass).get("__init__")
        if raw is None:
            continue
        fn, _ = _unwrap(raw)
        if fn is None:
            continue
        return _describe("new", fn, False, klass.__name__)
    return None
