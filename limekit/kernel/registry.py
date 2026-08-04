"""The single source of truth: dotted path -> class.

Generators for limekit.lua, the LSP stubs and manifest.py all walk this.
"""

from limekit.kernel.errors import RegistryError


class Registry:
    def __init__(self):
        self._by_path = {}

    def register(self, path, cls):
        if "." not in path:
            raise RegistryError(
                f"{path!r} is not a dotted path; expected 'module.Name'"
            )
        existing = self._by_path.get(path)
        if existing is not None and existing is not cls:
            raise RegistryError(
                f"{path!r} is already registered to {existing.__name__}"
            )
        self._by_path[path] = cls

    def get(self, path):
        try:
            return self._by_path[path]
        except KeyError:
            raise RegistryError(f"nothing registered at {path!r}") from None

    def modules(self):
        """Group registrations by their module prefix, for Lua's require()."""
        grouped = {}
        for path, cls in self._by_path.items():
            module, _, name = path.rpartition(".")
            grouped.setdefault(module, {})[name] = cls
        return grouped

    def paths(self):
        return tuple(sorted(self._by_path))

    def all(self):
        return tuple(self._by_path.values())

    def clear(self):
        self._by_path.clear()

    def clear_path(self, path):
        self._by_path.pop(path, None)


registry = Registry()
