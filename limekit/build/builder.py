"""
Limekit App Builder
Packages Limekit projects into standalone executables using PyInstaller

Source Code Protection:
- Lua scripts are compiled to bytecode before packaging
- Bytecode is embedded within the executable
- Original .lua files are not included in the distribution
"""

import os
import sys
import shutil
import tempfile
import subprocess
from typing import Optional, Dict, Any, Tuple

from limekit.build.constants import BUILD_DIR_NAME, DIST_DIR_NAME
from limekit.build.config import ConfigLoader, BuildConfig
from limekit.build.validator import ProjectValidator
from limekit.build.lua_compiler import LuaCompiler
from limekit.build.version_info import VersionInfoGenerator
from limekit.build.entry_script import EntryScriptGenerator
from limekit.build.spec_generator import SpecGenerator


class AppBuilder:
    """Builds Limekit projects into standalone executables."""

    def __init__(
        self,
        project_path: str,
        output_dir: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ):
        self.project_path = os.path.abspath(project_path)
        self.output_dir = output_dir or os.path.join(self.project_path, DIST_DIR_NAME)
        self.build_dir = os.path.join(self.project_path, BUILD_DIR_NAME)
        self.scripts_dir = os.path.join(self.project_path, "scripts")

        # Load configuration
        self.config_loader = ConfigLoader(self.project_path)
        self.config = self.config_loader.load(options)

        # Apply console mode from options if provided
        if options and options.get("console") is not None:
            self.config.console_mode = options["console"]

    def validate_project(self) -> Tuple[bool, list]:
        """Validate the project structure before building."""
        validator = ProjectValidator(self.project_path)
        return validator.validate_simple()

    def build(self, console_mode: bool = False) -> Tuple[bool, str, Optional[str]]:
        """
        Build the project into a standalone executable.

        Args:
            console_mode: If True, show console window. If False, windowed mode.

        Returns:
            tuple: (success: bool, message: str, output_path: str or None)
        """
        self.config.console_mode = console_mode

        # Validate project
        valid, errors = self.validate_project()
        if not valid:
            return False, f"Project validation failed: {'; '.join(errors)}", None

        # Create temporary build directory
        temp_dir = tempfile.mkdtemp(prefix="limekit_build_")

        try:
            # Step 1: Compile Lua scripts to bytecode
            print("Compiling Lua scripts...")
            temp_scripts = os.path.join(temp_dir, "scripts")
            compiler = LuaCompiler(self.scripts_dir)
            if not compiler.compile_to_directory(temp_scripts):
                return False, "Failed to compile Lua scripts", None

            # Step 2: Create entry script for frozen app
            print("Creating entry point...")
            entry_generator = EntryScriptGenerator(temp_dir, self.project_path)
            entry_script = entry_generator.generate()

            # Step 3: Generate Windows version info (if on Windows)
            version_file = None
            if sys.platform == "win32":
                version_generator = VersionInfoGenerator(self.config)
                version_file = version_generator.generate(temp_dir)

            # Step 4: Generate spec file
            print("Generating build configuration...")
            spec_generator = SpecGenerator(self.project_path, self.config, temp_dir)
            spec_path = spec_generator.generate(entry_script, version_file)

            # Step 5: Run PyInstaller
            print("Building executable...")
            result = self._run_pyinstaller(spec_path)

            if not result[0]:
                return result

            # Get output path
            output_path = self._get_output_path()

            if os.path.exists(output_path):
                return True, "Build completed successfully", output_path
            else:
                return False, "Build completed but executable not found", None

        except Exception as e:
            return False, f"Build error: {str(e)}", None

        finally:
            # Cleanup temporary directory
            self._cleanup_temp_dir(temp_dir)

    def _run_pyinstaller(self, spec_path: str) -> Tuple[bool, str, Optional[str]]:
        """Run PyInstaller with the generated spec file."""
        try:
            result = subprocess.run(
                [
                    sys.executable, "-m", "PyInstaller",
                    "--distpath", self.output_dir,
                    "--workpath", self.build_dir,
                    "--clean",
                    "--noconfirm",
                    spec_path
                ],
                capture_output=True,
                text=True,
                cwd=self.project_path
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                return False, f"PyInstaller build failed: {error_msg}", None

            return True, "PyInstaller completed", None

        except Exception as e:
            return False, f"PyInstaller error: {str(e)}", None

    def _get_output_path(self) -> str:
        """Get the expected output executable path."""
        if sys.platform == "win32":
            exe_name = f"{self.config.name}.exe"
        else:
            exe_name = self.config.name

        # Folder mode nests the exe under dist/<name>/; onefile puts it in dist/.
        if getattr(self.config, "onefile", True):
            return os.path.join(self.output_dir, exe_name)
        return os.path.join(self.output_dir, self.config.name, exe_name)

    def _cleanup_temp_dir(self, temp_dir: str) -> None:
        """Clean up temporary build directory."""
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass

    def clean(self) -> None:
        """Clean build artifacts."""
        dirs_to_clean = [self.build_dir, self.output_dir]

        for dir_path in dirs_to_clean:
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                    print(f"Cleaned: {dir_path}")
                except Exception as e:
                    print(f"Failed to clean {dir_path}: {e}")
