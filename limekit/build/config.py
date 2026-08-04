"""
Build Configuration
Handles loading and managing build configuration from app.json and options
"""

import os
import json
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from limekit.build.constants import (
    DEFAULT_APP_NAME,
    DEFAULT_APP_VERSION,
    IMAGES_DIR_NAME,
    APP_JSON_NAME,
)


@dataclass
class BuildConfig:
    """Configuration for building a Limekit application."""

    # App metadata
    name: str = DEFAULT_APP_NAME
    version: str = DEFAULT_APP_VERSION
    author: str = ""
    copyright: str = ""
    description: str = ""
    icon: Optional[str] = None

    # Build settings
    console_mode: bool = False
    onefile: bool = True  # True = single exe, False = folder with exe + dependencies

    # Raw app.json content (for additional fields)
    raw_config: Dict[str, Any] = field(default_factory=dict)


class ConfigLoader:
    """Loads build configuration from project files and options."""

    def __init__(self, project_path: str):
        self.project_path = os.path.abspath(project_path)
        self.images_dir = os.path.join(self.project_path, IMAGES_DIR_NAME)
        self.app_json_path = os.path.join(self.project_path, APP_JSON_NAME)

    def load(self, options: Optional[Dict[str, Any]] = None) -> BuildConfig:
        """
        Load build configuration from app.json and apply options overrides.

        Args:
            options: Optional dictionary of options to override app.json values

        Returns:
            BuildConfig with all settings applied
        """
        options = options or {}
        config = BuildConfig()

        # First, load from app.json
        self._load_from_app_json(config)

        # Then apply options overrides
        self._apply_options(config, options)

        # Find icon if not specified
        if not config.icon:
            config.icon = self._find_default_icon()

        return config

    def _load_from_app_json(self, config: BuildConfig) -> bool:
        """Load configuration from app.json file."""
        if not os.path.exists(self.app_json_path):
            return False

        try:
            with open(self.app_json_path, "r", encoding="utf-8") as f:
                app_json = json.load(f)

            config.raw_config = app_json
            project = app_json.get("project", {})

            config.name = project.get("name", DEFAULT_APP_NAME)
            config.version = project.get("version", DEFAULT_APP_VERSION)
            config.author = project.get("author", "")
            config.copyright = project.get("copyright", "")
            config.description = project.get("description", "")

            return True

        except Exception as e:
            from limekit.core.error_handler import warn
            warn(f"Error loading app.json: {e}", "BuildConfig")
            return False

    def _apply_options(self, config: BuildConfig, options: Dict[str, Any]) -> None:
        """Apply options dictionary to override config values."""
        if options.get("name"):
            config.name = options["name"]
        if options.get("version"):
            config.version = options["version"]
        if options.get("author"):
            config.author = options["author"]
        if options.get("copyright"):
            config.copyright = options["copyright"]
        if options.get("description"):
            config.description = options["description"]
        if options.get("icon") and os.path.exists(options["icon"]):
            config.icon = options["icon"]
        if options.get("console") is not None:
            config.console_mode = options["console"]
        if options.get("onefile") is not None:
            config.onefile = options["onefile"]

    def _find_default_icon(self) -> Optional[str]:
        """Look for default icon files in the images directory."""
        if not os.path.exists(self.images_dir):
            return None

        # Check for .ico first (Windows), then .png
        icon_candidates = ["app.ico", "icon.ico", "app.png", "icon.png"]

        for icon_name in icon_candidates:
            icon_path = os.path.join(self.images_dir, icon_name)
            if os.path.exists(icon_path):
                return icon_path

        return None
