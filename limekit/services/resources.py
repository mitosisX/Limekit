"""Project resource resolution: images/scripts/misc paths and app.json routes.

Ports limekit/utils/path.py and limekit/core/routing/routes.py (1.x) to the
2.0 service-layer pattern. The project root is not known at import time (it
is only known once a LimekitApp boots), so it lives in a module-level slot
set by `set_project_root`, mirroring how `bridge/convert.py` wires
`set_runtime`.
"""

import json
from pathlib import Path

from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError, ProjectError, RouteError

_project_root = None

_DIRS = {"images": "images", "scripts": "scripts", "misc": "misc"}


def set_project_root(path):
    """Called by LimekitApp.boot() once the project path is known."""
    global _project_root
    _project_root = Path(path)


def _require_root():
    if _project_root is None:
        raise ProjectError(
            "no project root is set; LimekitApp.boot() must run before "
            "res.Resources is used"
        )
    return _project_root


def _resource_path(marker, resource):
    directory = _DIRS.get(marker)
    if directory is None:
        raise RouteError(
            f"unknown resource marker {marker!r}; expected one of: "
            f"{', '.join(sorted(_DIRS))}"
        )
    root = _require_root()
    return str((root / directory / resource))


def _load_routes():
    root = _require_root()
    app_json = root / "app.json"
    if not app_json.is_file():
        raise ProjectError(f"no app.json found at {app_json}")
    try:
        data = json.loads(app_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProjectError(f"could not read app.json: {exc}") from exc
    return data.get("project", {}).get("routes", {}) or {}


def _resolve_marked(value, key):
    """Split a "marker::resource" string and resolve it to a real path."""
    if "::" not in value:
        raise RouteError(
            f"route {key!r} resolves to {value!r}, which has no "
            f"'marker::resource' marker"
        )
    marker, resource = value.split("::", 1)
    return _resource_path(marker, resource)


def _resolve_route(key, routes):
    """Resolve a route key against app.json's routes block.

    Two shapes, ported from 1.x:

    - `key` with no "::" is a `single` route: `routes.single[key]` must be a
      "marker::resource" string, e.g. `"images::app.png"`.
    - `key` of the form `"group::item"` is a `group` route:
      `routes.group[group]` is a table of items. If that table declares a
      `group_label`, every item value is a bare resource name resolved
      against that one marker (Exempt Individual Marking, EIM) -- 1.x
      documented this but never actually implemented it (the code always
      required a per-item marker even when group_label was present, which
      made group_label dead weight). This implementation makes EIM work:
      that is a completion of a documented, unimplemented feature, not a
      reproduction of a bug. Without group_label, each item value must carry
      its own "marker::resource" string, same as a single route.
    """
    if "::" in key:
        group_key, _, item_key = key.partition("::")
        group = routes.get("group", {}).get(group_key)
        if group is None:
            raise RouteError(f"no route group named {group_key!r}")
        if item_key not in group:
            raise RouteError(f"no item {item_key!r} in route group {group_key!r}")
        value = group[item_key]
        label = group.get("group_label")
        if label:
            return _resource_path(label, value)
        return _resolve_marked(value, key)

    value = routes.get("single", {}).get(key)
    if value is None:
        raise RouteError(f"no route named {key!r}")
    return _resolve_marked(value, key)


class Resources(LimeObject):
    __lime__ = "res.Resources"

    @staticmethod
    def images(name):
        if not isinstance(name, str):
            raise BridgeError(f"expected a string resource name, got {name!r}")
        return _resource_path("images", name)

    @staticmethod
    def scripts(name):
        if not isinstance(name, str):
            raise BridgeError(f"expected a string resource name, got {name!r}")
        return _resource_path("scripts", name)

    @staticmethod
    def misc(name):
        if not isinstance(name, str):
            raise BridgeError(f"expected a string resource name, got {name!r}")
        return _resource_path("misc", name)

    @staticmethod
    def route(key):
        if not isinstance(key, str):
            raise BridgeError(f"expected a string route key, got {key!r}")
        routes = _load_routes()
        if not routes:
            raise RouteError("no routes declared in app.json")
        return _resolve_route(key, routes)
