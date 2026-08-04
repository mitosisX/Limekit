"""
Version Info Generator
Creates Windows version info file for executables
"""

import os
import sys
from typing import Optional, Tuple

from limekit.build.config import BuildConfig


class VersionInfoGenerator:
    """Generates Windows version info file for PyInstaller."""

    def __init__(self, config: BuildConfig):
        self.config = config

    def generate(self, output_dir: str) -> Optional[str]:
        """
        Generate version info file for Windows.

        Args:
            output_dir: Directory to write the version file

        Returns:
            Path to generated file, or None if not on Windows
        """
        if sys.platform != "win32":
            return None

        version_tuple = self._parse_version()
        content = self._create_content(version_tuple)

        version_path = os.path.join(output_dir, "version_info.txt")
        with open(version_path, "w", encoding="utf-8") as f:
            f.write(content)

        return version_path

    def _parse_version(self) -> Tuple[int, int, int, int]:
        """Parse version string into a 4-tuple of integers."""
        version_parts = self.config.version.split(".")

        # Pad to 4 parts
        while len(version_parts) < 4:
            version_parts.append("0")

        # Convert to integers, defaulting to 0 for non-numeric
        result = []
        for part in version_parts[:4]:
            try:
                result.append(int(part))
            except ValueError:
                result.append(0)

        return tuple(result)

    def _create_content(self, version_tuple: Tuple[int, int, int, int]) -> str:
        """Create the version info file content."""
        return f'''# UTF-8
VSVersionInfo(
    ffi=FixedFileInfo(
        filevers={version_tuple},
        prodvers={version_tuple},
        mask=0x3f,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        StringFileInfo(
            [
                StringTable(
                    u'040904B0',
                    [
                        StringStruct(u'CompanyName', u'{self.config.author}'),
                        StringStruct(u'FileDescription', u'{self.config.description}'),
                        StringStruct(u'FileVersion', u'{self.config.version}'),
                        StringStruct(u'InternalName', u'{self.config.name}'),
                        StringStruct(u'LegalCopyright', u'{self.config.copyright}'),
                        StringStruct(u'OriginalFilename', u'{self.config.name}.exe'),
                        StringStruct(u'ProductName', u'{self.config.name}'),
                        StringStruct(u'ProductVersion', u'{self.config.version}'),
                    ]
                )
            ]
        ),
        VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
    ]
)
'''


def create_version_info(config: BuildConfig, output_dir: str) -> Optional[str]:
    """
    Convenience function to create version info file.

    Args:
        config: Build configuration
        output_dir: Directory to write version file

    Returns:
        Path to version file, or None if not on Windows
    """
    generator = VersionInfoGenerator(config)
    return generator.generate(output_dir)
