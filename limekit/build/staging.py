"""What a build ships: the project folder, as source, minus what never ships.

This replaced two things. A list of folders to bundle (`scripts/`,
`images/`, `misc/`, `app.json`, `.require`), which silently left out anything
else a project kept -- a `data/` folder, a bundled database. And a `luac`
pass that compiled scripts to bytecode under their `.lua` names whenever a
`luac` was on PATH: the 2.0 entry point reads `main.lua` as UTF-8 text and
failed on the bytecode, a failed compile was ignored, and a system `luac` may
not be the Lua 5.4 that lupa runs. Bytecode never hid anything anyway; it
decompiles readily.
"""

import shutil
from pathlib import Path

# Never shipped, wherever they appear.
_ANYWHERE = {".git", ".svn", ".hg", "__pycache__", ".preview", ".idea", ".vscode"}
# Never shipped at the project's top level: the build's own output. A
# `scripts/build/` folder of the user's is just a folder.
_TOP_LEVEL = {"build", "dist"}


def stage_project(project_path, dest, exclude=()):
    """Copy the project into `dest`, skipping junk and any path in `exclude`.

    `exclude` takes the build's output and work folders when a caller has
    put them somewhere other than the default `build/` and `dist/`.
    """
    root = Path(project_path).resolve()
    skip = {Path(p).resolve() for p in exclude}

    def ignore(directory, names):
        here = Path(directory).resolve()
        dropped = {n for n in names if n in _ANYWHERE or n.endswith(".spec")}
        if here == root:
            dropped |= {n for n in names if n in _TOP_LEVEL}
        dropped |= {n for n in names if (here / n).resolve() in skip}
        return dropped

    shutil.copytree(root, dest, ignore=ignore)
    return Path(dest)
