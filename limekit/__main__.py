"""Console entry point. The only place sys.exit is called."""

import sys

from limekit.kernel.app import LimekitApp
from limekit.kernel.errors import LimekitError


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("usage: python -m limekit <project-path>", file=sys.stderr)
        return 2

    app = LimekitApp(argv[0], argv=argv)
    app.boot()

    try:
        app.load_project()
    except LimekitError as error:
        # A mistake in someone's Lua is not a bug in the interpreter, and
        # showing them a Python traceback through lupa says otherwise -- the
        # one line that names their file and line was buried at the bottom of
        # forty. LuaError already carries source and line structurally.
        print(f"{error}", file=sys.stderr)
        return 1

    return app.run()


if __name__ == "__main__":
    sys.exit(main())
