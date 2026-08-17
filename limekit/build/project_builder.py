"""
Limekit Project Builder -- 1.x engine binding.

The build logic itself moved to `limekit/build/runner.py`, which is
engine-neutral, so the 2.0 `sys.ProjectBuilder` service can reuse it without
dragging in `EnginePart`. This class is the thin 1.x binding that exposes it
to Lua as the `__appBuild` global.
"""

from limekit.build.runner import BuildProcess

# EnginePart is a genuine 1.x dependency, not incidental: this class is what
# Lua's `app.buildProject(...)` resolves to, and that global is installed by
# the 1.x engine. Limer itself is still a 1.x app, so its Build button reaches
# the builder through here. It goes when Limer is ported.
from limekit.engine.parts import EnginePart


class ProjectBuilder(BuildProcess, EnginePart):
    """QProcess-based project builder that lets Limer monitor build progress.

    Exposes the same callback pattern as ProjectRunner for consistency. Every
    method comes from BuildProcess; this class exists only to register the
    `__appBuild` name with the 1.x engine.
    """

    name = "__appBuild"

    def __init__(self, project_path: str, options=None):
        BuildProcess.__init__(self, project_path, options)
