"""Standard Qt dialogs exposed to Lua as `require("limekit.ui").Dialogs`.

Ports limekit/components/dialogs/** (1.x) to the 2.0 service-layer pattern.
Every method returns a Lua-friendly Python value (or None on cancel) --
never a raw Qt type, and never raises just because a user closed a dialog.
"""

from PySide6.QtWidgets import (
    QColorDialog, QFileDialog, QFontDialog, QInputDialog, QMessageBox,
)

from limekit.kernel.bridge.convert import as_mapping, as_sequence, to_lua
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import method

_ICONS = {
    "none": QMessageBox.Icon.NoIcon,
    "question": QMessageBox.Icon.Question,
    "information": QMessageBox.Icon.Information,
    "warning": QMessageBox.Icon.Warning,
    "critical": QMessageBox.Icon.Critical,
}


def _message(parent, title, message, icon, buttons=QMessageBox.StandardButton.Ok):
    box = QMessageBox(parent)
    box.setWindowTitle(str(title))
    box.setText(str(message))
    box.setIcon(_ICONS.get(str(icon).lower(), QMessageBox.Icon.NoIcon))
    box.setStandardButtons(buttons)
    return box.exec()


def _filters_to_qt(filters):
    """{"Images": {"png", "jpg"}} -> "Images (*.png *.jpg)"."""
    if not filters:
        return ""
    try:
        pairs = as_mapping(filters).items()
    except BridgeError:
        raise
    except (TypeError, ValueError) as exc:
        raise BridgeError(f"expected a table of filters, got {filters!r}") from exc

    parts = []
    for label, extensions in pairs:
        exts = as_sequence(extensions)
        globs = " ".join(
            f"*{ext if ext.startswith('.') else '.' + ext}" for ext in exts
        )
        parts.append(f"{label} ({globs})" if globs else f"{label} (*)")
    return ";;".join(parts)


class Dialogs(LimeObject):
    __lime__ = "ui.Dialogs"

    # -- message boxes --------------------------------------------------

    @staticmethod
    @method({"parent": "any", "title": "string", "message": "string"}, doc="A plain message with no icon. Returns nil when dismissed.")
    def alert(parent, title, message):
        _message(parent, title, message, "none")
        return None

    @staticmethod
    @method({"parent": "any", "title": "string", "message": "string"}, doc="An information message.")
    def info(parent, title, message):
        _message(parent, title, message, "information")
        return None

    @staticmethod
    @method({"parent": "any", "title": "string", "message": "string"}, doc="A warning message.")
    def warning(parent, title, message):
        _message(parent, title, message, "warning")
        return None

    @staticmethod
    @method({"parent": "any", "title": "string", "message": "string"}, doc="An error message.")
    def critical(parent, title, message):
        _message(parent, title, message, "critical")
        return None

    @staticmethod
    @method({"parent": "any", "title": "string", "message": "string"}, returns="boolean", doc="Asks a yes/no question.")
    def question(parent, title, message):
        result = _message(
            parent, title, message, "question",
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        return result == QMessageBox.StandardButton.Yes

    # -- text/number input ------------------------------------------------

    @staticmethod
    @method({"parent": "any", "title": "string", "label": "string", "text": "string"}, returns="string", doc="Asks for a single line of text. Returns nil if cancelled.")
    def textInput(parent, title, label, text=""):
        value, ok = QInputDialog.getText(parent, str(title), str(label), text=str(text))
        return value if ok else None

    @staticmethod
    @method({"parent": "any", "title": "string", "label": "string", "text": "string"}, returns="string", doc="Asks for several lines of text. Returns nil if cancelled.")
    def multilineInput(parent, title, label, text=""):
        value, ok = QInputDialog.getMultiLineText(
            parent, str(title), str(label), str(text)
        )
        return value if ok else None

    @staticmethod
    @method({"parent": "any", "title": "string", "label": "string", "items": "string[]", "index": "integer"}, returns="string", doc="Asks the user to pick from a list. index is 1-based. Returns nil if cancelled.")
    def comboBoxInput(parent, title, label, items, index=1):
        options = as_sequence(items)
        if not options:
            raise BridgeError("comboBoxInput requires at least one item")
        # Lua is 1-indexed; QInputDialog.getItem wants a 0-indexed default.
        try:
            zero_index = int(index) - 1
        except (TypeError, ValueError) as exc:
            raise BridgeError(f"expected a numeric index, got {index!r}") from exc
        if not 0 <= zero_index < len(options):
            zero_index = 0
        value, ok = QInputDialog.getItem(
            parent, str(title), str(label), options, zero_index, False
        )
        return value if ok else None

    @staticmethod
    @method({"parent": "any", "title": "string", "label": "string", "value": "integer", "min_value": "integer", "max_value": "integer", "step": "integer"}, returns="integer", doc="Asks for a whole number. Returns nil if cancelled.")
    def integerInput(parent, title, label, value=0, min_value=-2147483647,
                      max_value=2147483647, step=1):
        result, ok = QInputDialog.getInt(
            parent, str(title), str(label), int(value), int(min_value),
            int(max_value), int(step),
        )
        return result if ok else None

    @staticmethod
    @method({"parent": "any", "title": "string", "label": "string", "value": "number", "min_value": "number", "max_value": "number", "decimals": "integer"}, returns="number", doc="Asks for a decimal number. Returns nil if cancelled.")
    def doubleInput(parent, title, label, value=0.0, min_value=-2147483647.0,
                     max_value=2147483647.0, decimals=2):
        result, ok = QInputDialog.getDouble(
            parent, str(title), str(label), float(value), float(min_value),
            float(max_value), int(decimals),
        )
        return result if ok else None

    # -- file / folder pickers --------------------------------------------

    @staticmethod
    @method({"parent": "any", "title": "string", "directory": "string", "filters": "table<string, string[]>"}, returns="string", doc="Asks for a file to open. filters maps a description to its extensions. Returns nil if cancelled.")
    def openFile(parent, title="", directory="", filters=None):
        path, _ = QFileDialog.getOpenFileName(
            parent, str(title), str(directory), _filters_to_qt(filters)
        )
        return path or None

    @staticmethod
    @method({"parent": "any", "title": "string", "directory": "string", "filters": "table<string, string[]>"}, returns="string", doc="Asks where to save a file. Returns nil if cancelled.")
    def saveFile(parent, title="", directory="", filters=None):
        path, _ = QFileDialog.getSaveFileName(
            parent, str(title), str(directory), _filters_to_qt(filters)
        )
        return path or None

    @staticmethod
    @method({"parent": "any", "title": "string", "directory": "string"}, returns="string", doc="Asks the user to choose a folder. Returns nil if cancelled.")
    def pickFolder(parent, title="", directory=""):
        path = QFileDialog.getExistingDirectory(
            parent, str(title), str(directory),
            QFileDialog.Option.ShowDirsOnly,
        )
        return path or None

    # -- color / font -----------------------------------------------------

    @staticmethod
    @method({"parent": "any", "initial": "any"}, returns="any", doc="Opens the colour picker. Returns nil if cancelled.")
    def pickColour(parent=None, initial=None):
        from limekit.kernel.coerce import Colour
        start = Colour(initial) if initial is not None else None
        colour = (
            QColorDialog.getColor(start, parent) if start is not None
            else QColorDialog.getColor(parent=parent)
        )
        if not colour.isValid():
            return None
        return to_lua({
            "r": colour.red(), "g": colour.green(), "b": colour.blue(),
            "hex": colour.name(),
        })

    @staticmethod
    @method({"parent": "any"}, returns="any", doc="Opens the font picker. Returns nil if cancelled.")
    def pickFont(parent=None):
        font, ok = QFontDialog.getFont(parent)
        if not ok:
            return None
        return to_lua({
            "family": font.family(),
            "pointSize": font.pointSize(),
            "bold": font.bold(),
            "italic": font.italic(),
        })
