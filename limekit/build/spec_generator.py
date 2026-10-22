"""
Spec File Generator
Generates PyInstaller spec files for Limekit applications
"""

import os
from typing import Optional, List, Tuple

from limekit.build.config import BuildConfig
from limekit.build.constants import HIDDEN_IMPORTS


class SpecGenerator:
    """Generates PyInstaller spec files for building Limekit applications."""

    def __init__(
        self,
        project_path: str,
        config: BuildConfig,
        temp_dir: str
    ):
        self.project_path = os.path.abspath(project_path)
        self.config = config
        self.temp_dir = temp_dir
        # builder.AppBuilder stages the whole project here (build/staging.py).
        self.staged_dir = os.path.join(self.temp_dir, "project")

    def generate(
        self,
        entry_script: str,
        version_file: Optional[str] = None
    ) -> str:
        """
        Generate PyInstaller spec file.

        Args:
            entry_script: Path to the entry script
            version_file: Optional path to Windows version info file

        Returns:
            Path to the generated spec file
        """
        spec_content = self._create_spec_content(entry_script, version_file)
        spec_path = os.path.join(self.temp_dir, f"{self.config.name}.spec")

        with open(spec_path, "w", encoding="utf-8") as f:
            f.write(spec_content)

        return spec_path

    def _normalize_path(self, path: str) -> str:
        """Convert Windows backslashes to forward slashes for spec file."""
        return path.replace('\\', '/')

    def _literal(self, path: str) -> str:
        """A path as Python source for the spec.

        repr(), not r'...': a raw literal cannot hold a quote, so a project
        in "Bob's App" produced a spec that did not parse.
        """
        return repr(self._normalize_path(str(path)))

    def _get_limekit_paths(self) -> Tuple[str, str]:
        """Get limekit package paths."""
        import limekit
        limekit_path = os.path.dirname(limekit.__file__)
        limekit_parent = os.path.dirname(limekit_path)
        return limekit_path, limekit_parent

    def _collect_data_files(self) -> List[Tuple[str, str]]:
        """Collect all data files to include in the build."""
        datas = []
        limekit_path, _ = self._get_limekit_paths()

        # The whole staged project, laid out at the bundle's root exactly as
        # it is on disk: folders keep their names, top-level files go to ".".
        if os.path.isdir(self.staged_dir):
            for entry in sorted(os.listdir(self.staged_dir)):
                path = os.path.join(self.staged_dir, entry)
                target = entry if os.path.isdir(path) else "."
                datas.append((self._literal(path), repr(target)))

        return datas

    def _format_hidden_imports(self) -> str:
        """Format hidden imports list for spec file."""
        return ", ".join([f"'{h}'" for h in HIDDEN_IMPORTS])

    def _create_spec_content(
        self,
        entry_script: str,
        version_file: Optional[str] = None
    ) -> str:
        """Create the PyInstaller spec file content."""
        limekit_path, limekit_parent = self._get_limekit_paths()

        # Collect data files
        datas = self._collect_data_files()
        datas_str = ",\n        ".join([f"({src}, {dst})" for src, dst in datas])

        # Hidden imports
        hidden_str = self._format_hidden_imports()

        # Icon configuration
        icon_line = ""
        if self.config.icon:
            icon_line = f"icon={self._literal(self.config.icon)},"

        # Version info (Windows only)
        version_line = ""
        if version_file:
            version_line = f"version={self._literal(version_file)},"

        # Console mode
        console_line = "True" if self.config.console_mode else "False"

        # Onefile mode
        onefile = getattr(self.config, 'onefile', True)

        # Normalize paths
        entry_script_literal = self._literal(entry_script)
        project_path_literal = self._literal(self.project_path)
        limekit_parent_literal = self._literal(limekit_parent)

        # Build EXE section based on onefile mode
        if onefile:
            exe_section = f'''
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{self.config.name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={console_line},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {icon_line}
    {version_line}
)
'''
        else:
            # Folder mode - separate exe and dependencies
            exe_section = f'''
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{self.config.name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={console_line},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {icon_line}
    {version_line}
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    a.zipfiles,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{self.config.name}',
)
'''

        return f'''# -*- mode: python ; coding: utf-8 -*-
# Limekit App Build Spec - Auto-generated

import sys
sys.path.insert(0, {limekit_parent_literal})

from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_all

block_cipher = None

# Collect all limekit submodules, datas, and binaries
limekit_datas, limekit_binaries, limekit_hiddenimports = collect_all('limekit')

# Additional hidden imports
hiddenimports = limekit_hiddenimports + [{hidden_str}]

a = Analysis(
    [{entry_script_literal}],
    pathex=[{project_path_literal}, {limekit_parent_literal}],
    binaries=limekit_binaries,
    datas=[
        {datas_str}
    ] + limekit_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
        'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
{exe_section}
'''


def generate_spec_file(
    project_path: str,
    config: BuildConfig,
    temp_dir: str,
    entry_script: str,
    version_file: Optional[str] = None
) -> str:
    """
    Convenience function to generate a spec file.

    Args:
        project_path: Path to the project
        config: Build configuration
        temp_dir: Temporary build directory
        entry_script: Path to entry script
        version_file: Optional Windows version info file

    Returns:
        Path to the generated spec file
    """
    generator = SpecGenerator(project_path, config, temp_dir)
    return generator.generate(entry_script, version_file)
