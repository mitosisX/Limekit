"""Explicit application lifecycle.

Nothing here runs at import time: constructing a LimekitApp is what creates
the QApplication, so the framework can be imported by tests and tooling.
"""

import sys
from pathlib import Path

from limekit.kernel.bridge.guard import reset_error_sink, set_error_sink
from limekit.kernel.bridge.runtime import LimeRuntime
from limekit.kernel.errors import ProjectError
from limekit.kernel.registry import registry


class LimekitApp:
    def __init__(self, project_path, *, argv=None, frozen=False):
        self.project_path = Path(project_path)
        self.argv = list(argv) if argv is not None else []
        self.frozen = frozen
        self.qt_app = None
        self.runtime = None
        self._errors = []

    # -- lifecycle ---------------------------------------------------------

    def boot(self):
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QApplication

        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        self.qt_app = QApplication.instance() or QApplication(self.argv)

        from limekit.kernel import manifest
        manifest.import_all()

        self.runtime = LimeRuntime(registry)
        self.runtime.install_modules()
        set_error_sink(self._on_error)
        return self

    def load_project(self):
        main = self.project_path / "scripts" / "main.lua"
        if not main.is_file():
            raise ProjectError(f"no main.lua found at {main}")

        self._set_lua_path()
        relative = main.relative_to(self.project_path).as_posix()
        self.runtime.execute(main.read_text(encoding="utf-8"), chunkname=relative)
        return self

    def run(self):
        if self.qt_app is None:
            raise ProjectError("boot() must be called before run()")
        return self.qt_app.exec()

    def shutdown(self):
        reset_error_sink()
        self.runtime = None
        self.qt_app = None

    # -- internals ---------------------------------------------------------

    def _set_lua_path(self):
        roots = [self.project_path / "scripts", self.project_path / "misc"]
        entries = []
        for root in roots:
            if not root.is_dir():
                continue
            for directory in [root, *(p for p in root.rglob("*") if p.is_dir())]:
                posix = directory.as_posix()
                entries.append(f"{posix}/?.lua")
                entries.append(f"{posix}/?/init.lua")
        if entries:
            joined = ";".join(dict.fromkeys(entries)) + ";"
            self.runtime.execute(
                f"package.path = {joined!r} .. package.path",
                chunkname="<limekit:package.path>",
            )

    def _on_error(self, error):
        self._errors.append(error)
        print(f"\n{error}", file=sys.stderr)

    @property
    def errors(self):
        return tuple(self._errors)

    # -- context manager ---------------------------------------------------

    def __enter__(self):
        return self.boot()

    def __exit__(self, *exc_info):
        self.shutdown()
        return False
