"""Console entry point. The only place sys.exit is called."""

import sys

from limekit.kernel.app import LimekitApp


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("usage: python -m limekit <project-path>", file=sys.stderr)
        return 2

    app = LimekitApp(argv[0], argv=argv)
    app.boot()
    app.load_project()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
