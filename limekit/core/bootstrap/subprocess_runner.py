"""Compatibility shim.

This module's contents moved to `limekit/launcher.py`, which is
engine-neutral -- the 2.0 build path and the `sys.ProjectRunner` service both
need `detect_api_version` and the runner, and reaching into `limekit/core/`
for them meant the new tree depended on the legacy one.

The names are re-exported here so the 1.x engine, and anything importing this
path directly, keeps working unchanged.
"""

from limekit.launcher import (                              # noqa: F401
    LEGACY_ENTRY,
    MODERN_ENTRY,
    ProjectRunner,
    detect_api_version,
    entry_for,
    python_command,
)

__all__ = [
    "LEGACY_ENTRY",
    "MODERN_ENTRY",
    "ProjectRunner",
    "detect_api_version",
    "entry_for",
    "python_command",
]
