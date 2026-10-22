"""
Entry Script Generator
Creates the entry point script for frozen Limekit applications
"""

import os


class EntryScriptGenerator:
    """Generates the entry point script for frozen applications.

    One engine, one entry point: 1.x projects are refused before a build
    gets this far (`builder.AppBuilder.build`).
    """

    ENTRY_SCRIPT_TEMPLATE = '''import sys
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
try:
    app.load_project()
except Exception as error:
    # A windowed build has no console, so an error here used to make the
    # app vanish without a word. Say what went wrong, and where.
    if sys.stderr:
        print(error, file=sys.stderr)
    from PySide6.QtWidgets import QMessageBox
    title = os.path.splitext(os.path.basename(sys.executable))[0] or "Error"
    QMessageBox.critical(None, title, f"This app could not start.\\n\\n{error}")
    sys.exit(1)
sys.exit(app.run())
'''

    def __init__(self, output_dir: str):
        self.output_dir = output_dir

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
            f.write(self.ENTRY_SCRIPT_TEMPLATE)

        return entry_path


def create_entry_script(output_dir: str, filename: str = "app_entry.py") -> str:
    """
    Convenience function to create entry script.

    Args:
        output_dir: Directory to write entry script
        filename: Name of the entry script file

    Returns:
        Path to the generated entry script
    """
    generator = EntryScriptGenerator(output_dir)
    return generator.generate(filename)
