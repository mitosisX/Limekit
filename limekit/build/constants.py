"""
Build Constants
Shared constants used across the build module
"""

# Hidden imports required for PyInstaller to bundle correctly
HIDDEN_IMPORTS = [
    # Limekit core
    "limekit",
    "limekit.runner",
    "limekit.core",
    "limekit.core.error_handler",
    "limekit.engine",
    "limekit.engine.app_engine",
    "limekit.engine.parts",
    "limekit.engine.globals",
    "limekit.engine.globals.global_engine",
    "limekit.engine.lifecycle",
    "limekit.engine.lifecycle.app",
    "limekit.engine.lifecycle.shutdown",
    # Components
    "limekit.components",
    "limekit.components.base",
    "limekit.components.base.widget_base",
    "limekit.components.widgets",
    "limekit.components.layouts",
    "limekit.components.dialogs",
    "limekit.components.menu",
    "limekit.components.toolbar",
    "limekit.components.dockable",
    # Utils and config
    "limekit.utils",
    "limekit.config",
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
    "qtmodern",
    "psutil",
    "emoji",
    "playsound",
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
