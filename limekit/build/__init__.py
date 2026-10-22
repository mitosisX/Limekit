# Limekit Build Module
# Handles packaging Limekit apps into standalone executables

from limekit.build.builder import AppBuilder
from limekit.build.config import BuildConfig, ConfigLoader
from limekit.build.validator import ProjectValidator, ValidationResult
from limekit.build.staging import stage_project
from limekit.build.version_info import VersionInfoGenerator, create_version_info
from limekit.build.entry_script import EntryScriptGenerator, create_entry_script
from limekit.build.spec_generator import SpecGenerator, generate_spec_file
from limekit.build.constants import (
    HIDDEN_IMPORTS,
    DEFAULT_APP_NAME,
    DEFAULT_APP_VERSION,
)

__all__ = [
    # Main builders
    "AppBuilder",
    # Configuration
    "BuildConfig",
    "ConfigLoader",
    # Validation
    "ProjectValidator",
    "ValidationResult",
    # What ships
    "stage_project",
    # Version info
    "VersionInfoGenerator",
    "create_version_info",
    # Entry script
    "EntryScriptGenerator",
    "create_entry_script",
    # Spec generation
    "SpecGenerator",
    "generate_spec_file",
    # Constants
    "HIDDEN_IMPORTS",
    "DEFAULT_APP_NAME",
    "DEFAULT_APP_VERSION",
]
