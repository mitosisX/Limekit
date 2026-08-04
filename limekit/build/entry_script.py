"""
Entry Script Generator
Creates the entry point script for frozen Limekit applications
"""

import os

from limekit.core.bootstrap.subprocess_runner import detect_api_version


class EntryScriptGenerator:
    """Generates the entry point script for frozen applications.

    Two engines, two entry points. A 2.0 project frozen with the 1.x entry
    script dies at startup with "module 'limekit.ui' not found", because the
    1.x engine injects flat globals and never populates package.preload --
    the same failure Limer hit when running (not building) a 2.0 project.

    The version is detected from the project exactly as the process runner
    detects it, so Run and Build cannot disagree about which engine a
    project targets.
    """

    MODERN_ENTRY_SCRIPT_TEMPLATE = '''import sys
import os

# Determine the project path based on execution context
if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

# require() must find bundled Lua files
original_path = os.environ.get('PATH', '')
os.environ['PATH'] = bundle_dir + os.pathsep + original_path

from limekit.kernel.app import LimekitApp

app = LimekitApp(bundle_dir, argv=sys.argv, frozen=True)
app.boot()
app.load_project()
sys.exit(app.run())
'''

    ENTRY_SCRIPT_TEMPLATE = '''import sys
import os

# Determine the project path based on execution context
if getattr(sys, 'frozen', False):
    # Running as compiled executable - use PyInstaller's _MEIPASS
    bundle_dir = sys._MEIPASS
else:
    # Running as script (shouldn't happen for built apps)
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

# Set up sys.argv so limekit runner knows where the project is
sys.argv = [sys.argv[0], bundle_dir]

# Patch lupa to find Lua files in the frozen bundle
# This ensures require() works in frozen apps
original_path = os.environ.get('PATH', '')
os.environ['PATH'] = bundle_dir + os.pathsep + original_path

# Import and run limekit
from limekit.runner import LimerApplication
app = LimerApplication()
app.run()
'''

    def __init__(self, output_dir: str, project_path: str = None):
        self.output_dir = output_dir
        # None keeps the 1.x template, which is what every existing caller
        # and every existing project already relies on.
        self.project_path = project_path

    def template_for(self, project_path):
        if project_path and detect_api_version(project_path) == "2.0":
            return self.MODERN_ENTRY_SCRIPT_TEMPLATE
        return self.ENTRY_SCRIPT_TEMPLATE

    def generate(self, filename: str = "app_entry.py") -> str:
        """
        Generate the entry script for the frozen application.

        Args:
            filename: Name of the entry script file

        Returns:
            Path to the generated entry script
        """
        entry_path = os.path.join(self.output_dir, filename)

        with open(entry_path, "w", encoding="utf-8") as f:
            f.write(self.template_for(self.project_path))

        return entry_path


def create_entry_script(output_dir: str, filename: str = "app_entry.py",
                        project_path: str = None) -> str:
    """
    Convenience function to create entry script.

    Args:
        output_dir: Directory to write entry script
        filename: Name of the entry script file
        project_path: The project being built; decides which engine's entry
            point is emitted. Omitting it keeps the 1.x default.

    Returns:
        Path to the generated entry script
    """
    generator = EntryScriptGenerator(output_dir, project_path)
    return generator.generate(filename)
