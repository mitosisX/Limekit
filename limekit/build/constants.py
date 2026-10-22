"""
Build Constants
Shared constants used across the build module
"""

# Hidden imports required for PyInstaller to bundle correctly.
#
# These matter more than they look: limekit/kernel/manifest.py reaches every
# widget module through importlib.import_module() over a list of strings,
# which PyInstaller's static analysis cannot follow. Without these, a frozen
# app can start and then fail at boot() with ModuleNotFoundError. Keep this
# list in step with manifest.MODULES -- or rather, with the packages
# containing them.
HIDDEN_IMPORTS = [
    "limekit",
    "limekit.kernel",
    "limekit.kernel.app",
    "limekit.kernel.manifest",
    "limekit.kernel.registry",
    "limekit.kernel.bridge",
    "limekit.kernel.bridge.runtime",
    "limekit.kernel.bridge.convert",
    "limekit.kernel.bridge.guard",
    "limekit.widgets",
    "limekit.layouts",
    "limekit.services",
    "limekit.charts",
    "limekit.toolkit",
    "limekit.runtime",
    "limekit.assets",
    # Lupa/Lua
    "lupa",
    "lupa.lua54",
    # PySide6
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtWidgets",
    "PySide6.QtGui",
    "PySide6.QtCharts",
    "PySide6.QtPrintSupport",
    "PySide6.QtSvg",
    # Other dependencies
    "sqlite3",
    "qt_material",
    "qdarkstyle",
    "qdarktheme",
    # Imported by services the manifest loads by name, so analysis never
    # reaches them on its own.
    "emoji",
    "psutil",
]

# Default app configuration values
DEFAULT_APP_NAME = "LimekitApp"
DEFAULT_APP_VERSION = "1.0"

# Build directory names
BUILD_DIR_NAME = "build"
DIST_DIR_NAME = "dist"

# Project structure
SCRIPTS_DIR_NAME = "scripts"
IMAGES_DIR_NAME = "images"
MISC_DIR_NAME = "misc"
APP_JSON_NAME = "app.json"
REQUIRE_FILE_NAME = ".require"

# Entry point
MAIN_LUA_NAME = "main.lua"
