"""
Lua Compiler
Compiles Lua scripts to bytecode for source code protection
"""

import os
import shutil
import subprocess
from typing import Optional


class LuaCompiler:
    """
    Compiles Lua scripts to bytecode for source code protection.

    Uses luac (Lua compiler) if available, otherwise copies scripts as-is.
    """

    def __init__(self, scripts_dir: str):
        self.scripts_dir = scripts_dir
        self._luac_available: Optional[bool] = None

    @property
    def luac_available(self) -> bool:
        """Check if Lua compiler (luac) is available on the system."""
        if self._luac_available is None:
            self._luac_available = self._check_luac()
        return self._luac_available

    def _check_luac(self) -> bool:
        """Check if luac command is available."""
        try:
            result = subprocess.run(
                ["luac", "-v"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def compile_to_directory(self, output_dir: str) -> bool:
        """
        Compile all Lua scripts to bytecode in the output directory.

        Args:
            output_dir: Directory to write compiled files to

        Returns:
            True if successful, False otherwise
        """
        try:
            os.makedirs(output_dir, exist_ok=True)

            for root, dirs, files in os.walk(self.scripts_dir):
                for file in files:
                    if file.endswith(".lua"):
                        src_file = os.path.join(root, file)
                        rel_path = os.path.relpath(src_file, self.scripts_dir)
                        dest_file = os.path.join(output_dir, rel_path)

                        # Create destination directory
                        os.makedirs(os.path.dirname(dest_file), exist_ok=True)

                        # Compile or copy
                        if self.luac_available:
                            self._compile_file(src_file, dest_file)
                        else:
                            shutil.copy2(src_file, dest_file)

            return True

        except Exception as e:
            from limekit.core.error_handler import warn
            warn(f"Error compiling Lua scripts: {e}", "LuaCompiler")
            return False

    def _compile_file(self, src: str, dest: str) -> bool:
        """
        Compile a single Lua file to bytecode.

        Args:
            src: Source Lua file path
            dest: Destination file path for bytecode

        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["luac", "-o", dest, src],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0

        except Exception:
            # Fallback: copy without compilation
            shutil.copy2(src, dest)
            return True

    def compile_single(self, src: str, dest: str) -> bool:
        """
        Compile a single Lua file.

        Args:
            src: Source Lua file path
            dest: Destination file path

        Returns:
            True if successful, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(dest), exist_ok=True)

            if self.luac_available:
                return self._compile_file(src, dest)
            else:
                shutil.copy2(src, dest)
                return True

        except Exception as e:
            from limekit.core.error_handler import warn
            warn(f"Error compiling {src}: {e}", "LuaCompiler")
            return False


def compile_scripts(scripts_dir: str, output_dir: str) -> bool:
    """
    Convenience function to compile all Lua scripts in a directory.

    Args:
        scripts_dir: Source scripts directory
        output_dir: Output directory for compiled scripts

    Returns:
        True if successful, False otherwise
    """
    compiler = LuaCompiler(scripts_dir)
    return compiler.compile_to_directory(output_dir)
