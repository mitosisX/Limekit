"""Explicit application lifecycle.

Nothing here runs at import time: constructing a LimekitApp is what creates
the QApplication, so the framework can be imported by tests and tooling.
"""

import sys
from pathlib import Path

from limekit.kernel import affinity
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

        # boot() runs on the GUI thread, so this is the thread every widget
        # will belong to. Recorded here so generated setters can catch a
        # worker thread touching one -- see kernel/affinity.py.
        affinity.set_gui_thread()

        from limekit.services import resources
        resources.set_project_root(self.project_path)

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
        self._stop_timers()
        self._stop_threads()
        reset_error_sink()
        affinity.reset()
        self.runtime = None
        self.qt_app = None

    @staticmethod
    def _stop_timers():
        """Stop any sys.Timer still ticking before the runtime goes away.

        Its callback lives in Lua; once the runtime is dropped, a timer that
        keeps firing reports "Internal C++ object already deleted" from
        somewhere the author has no way to connect back to their code.
        """
        for timer in affinity.live_timers():
            timer.stop()

    @staticmethod
    def _stop_threads(msecs=5000):
        """Wait for any sys.Thread still running before tearing down.

        Qt aborts the process outright if a QThread is destroyed while it is
        still running, so an app that shut down with a worker in flight died
        with a crash rather than an exit code. Waiting here means the last
        thing a project does cannot be to fall over.
        """
        for thread in affinity.live_workers():
            thread.quit()
            thread.wait(msecs)

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
