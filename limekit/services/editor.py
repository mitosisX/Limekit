"""A project's `.luarc.json`: what makes an editor understand Limekit.

lua-language-server -- behind the Lua extension in VS Code, and Neovim's
Lua setup -- reads `.luarc.json` from a project's folder. Pointed at the
stubs that ship inside Limekit, it completes `ui.Button(`, lists a
button's methods and flags `button:setTxt`. Nothing to install and nothing
to configure: Limer writes the file when it creates or opens a project.

The stubs live inside Limer's own folder, so the path in the file is only
right until Limer is unzipped somewhere else. Writing again on every open
replaces the dead path, and leaves alone anything the author added.
"""

import json
import os

from limekit.kernel.declarative import LimeObject
from limekit.kernel.spec import method

STUBS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "runtime", "lua", "stubs").replace("\\", "/")

CONFIG = ".luarc.json"

# How a Limekit stubs path ends, wherever the Limer holding it was unzipped.
_STUBS_SUFFIX = "/limekit/runtime/lua/stubs"


def _is_limekit_stubs(entry):
    return isinstance(entry, str) and \
        entry.replace("\\", "/").rstrip("/").endswith(_STUBS_SUFFIX)


def _with_current_stubs(library):
    kept = [entry for entry in library if not _is_limekit_stubs(entry)]
    return kept + [STUBS]


def write_config(project):
    """Create or refresh `project/.luarc.json`. True if the file changed."""
    if not os.path.isdir(project):
        return False
    path = os.path.join(project, CONFIG)

    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as handle:
                config = json.load(handle)
        except (OSError, ValueError):
            return False            # theirs, and not ours to rewrite
        if not isinstance(config, dict):
            return False
    else:
        config = {
            "$schema": "https://raw.githubusercontent.com/LuaLS/vscode-lua/master/setting/schema.json",
            "runtime.version": "Lua 5.4",
        }

    before = json.dumps(config, sort_keys=True)
    nested = config.get("workspace")
    if isinstance(nested, dict) and "library" in nested:
        nested["library"] = _with_current_stubs(nested.get("library") or [])
    else:
        config["workspace.library"] = _with_current_stubs(config.get("workspace.library") or [])

    if os.path.exists(path) and json.dumps(config, sort_keys=True) == before:
        return False
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(config, handle, indent=2)
        handle.write("\n")
    return True


class EditorSetup(LimeObject):
    """`sys.EditorSetup`: editor completion for a project, with no setup."""

    __lime__ = "sys.EditorSetup"

    @staticmethod
    @method({"project": "string"}, returns="boolean",
            doc="Writes or refreshes the project's .luarc.json so editors "
                "using lua-language-server complete Limekit's API. Returns "
                "true if the file changed. Leaves a file it cannot read alone.")
    def write(project):
        return write_config(str(project))

    @staticmethod
    @method(returns="string",
            doc="The folder holding Limekit's Lua Language Server stubs.")
    def getStubsFolder():
        return STUBS
