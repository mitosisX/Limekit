"""
Project Validator
Validates Limekit project structure before building
"""

import os
from dataclasses import dataclass, field
from typing import List, Tuple

from limekit.build.constants import (
    SCRIPTS_DIR_NAME,
    APP_JSON_NAME,
    MAIN_LUA_NAME,
)


@dataclass
class ValidationResult:
    """Result of project validation."""

    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        """Add an error and mark as invalid."""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add a warning (doesn't affect validity)."""
        self.warnings.append(message)


class ProjectValidator:
    """Validates Limekit project structure for building."""

    def __init__(self, project_path: str):
        self.project_path = os.path.abspath(project_path)
        self.scripts_dir = os.path.join(self.project_path, SCRIPTS_DIR_NAME)
        self.app_json_path = os.path.join(self.project_path, APP_JSON_NAME)

    def validate(self) -> ValidationResult:
        """
        Validate the project structure.

        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult()

        # Check project path exists
        if not os.path.exists(self.project_path):
            result.add_error(f"Project path does not exist: {self.project_path}")
            return result  # Can't continue without project path

        # Check for app.json
        if not os.path.exists(self.app_json_path):
            result.add_error("Missing app.json configuration file")

        # Check for scripts directory
        if not os.path.exists(self.scripts_dir):
            result.add_error("Missing scripts directory")
        else:
            # Check for main.lua entry point
            main_lua = os.path.join(self.scripts_dir, MAIN_LUA_NAME)
            if not os.path.exists(main_lua):
                result.add_error(f"Missing {MAIN_LUA_NAME} entry point in scripts directory")

            # Check if scripts directory is empty
            lua_files = self._count_lua_files()
            if lua_files == 0:
                result.add_warning("No Lua files found in scripts directory")

        return result

    def validate_simple(self) -> Tuple[bool, List[str]]:
        """
        Simple validation returning (success, errors) tuple.
        For backwards compatibility with existing code.
        """
        result = self.validate()
        return result.is_valid, result.errors

    def _count_lua_files(self) -> int:
        """Count the number of Lua files in scripts directory."""
        count = 0
        for root, dirs, files in os.walk(self.scripts_dir):
            for file in files:
                if file.endswith(".lua"):
                    count += 1
        return count

    def get_lua_files(self) -> List[str]:
        """Get all Lua files in the scripts directory."""
        lua_files = []
        for root, dirs, files in os.walk(self.scripts_dir):
            for file in files:
                if file.endswith(".lua"):
                    lua_files.append(os.path.join(root, file))
        return lua_files
