from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from limekit.framework.core.engine.parts import EnginePart


class KeyBoard(EnginePart):
    """Utility class to check if a pressed key matches a given string (e.g., 'A', 'Enter', 'Ctrl+A')."""

    # Mapping of string keys to Qt.Key_* constants
    KEY_MAP = {
        # Letters (A-Z)
        **{chr(k): getattr(Qt, f"Key_{chr(k)}") for k in range(ord("A"), ord("Z") + 1)},
        # Numbers (0-9)
        **{str(k): getattr(Qt, f"Key_{k}") for k in range(0, 10)},
        # Function keys (F1-F24)
        **{f"F{k}": getattr(Qt, f"Key_F{k}") for k in range(1, 25)},
        # Navigation & Special Keys
        "Enter": Qt.Key_Return,
        "Return": Qt.Key_Return,
        "Escape": Qt.Key_Escape,
        "Tab": Qt.Key_Tab,
        "Backspace": Qt.Key_Backspace,
        "Delete": Qt.Key_Delete,
        "Insert": Qt.Key_Insert,
        "Home": Qt.Key_Home,
        "End": Qt.Key_End,
        "PageUp": Qt.Key_PageUp,
        "PageDown": Qt.Key_PageDown,
        "Left": Qt.Key_Left,
        "Right": Qt.Key_Right,
        "Up": Qt.Key_Up,
        "Down": Qt.Key_Down,
        "Space": Qt.Key_Space,
        "CapsLock": Qt.Key_CapsLock,
        "NumLock": Qt.Key_NumLock,
        "ScrollLock": Qt.Key_ScrollLock,
        "Pause": Qt.Key_Pause,
        "Print": Qt.Key_Print,
        "SysReq": Qt.Key_SysReq,
        "Menu": Qt.Key_Menu,
        # Punctuation & Symbols
        "`": Qt.Key_QuoteLeft,
        "~": Qt.Key_AsciiTilde,
        "!": Qt.Key_Exclam,
        "@": Qt.Key_At,
        "#": Qt.Key_NumberSign,
        "$": Qt.Key_Dollar,
        "%": Qt.Key_Percent,
        "^": Qt.Key_AsciiCircum,
        "&": Qt.Key_Ampersand,
        "*": Qt.Key_Asterisk,
        "(": Qt.Key_ParenLeft,
        ")": Qt.Key_ParenRight,
        "-": Qt.Key_Minus,
        "_": Qt.Key_Underscore,
        "=": Qt.Key_Equal,
        "+": Qt.Key_Plus,
        "[": Qt.Key_BracketLeft,
        "]": Qt.Key_BracketRight,
        "{": Qt.Key_BraceLeft,
        "}": Qt.Key_BraceRight,
        "\\": Qt.Key_Backslash,
        "|": Qt.Key_Bar,
        ";": Qt.Key_Semicolon,
        ":": Qt.Key_Colon,
        "'": Qt.Key_Apostrophe,
        '"': Qt.Key_QuoteDbl,
        ",": Qt.Key_Comma,
        "<": Qt.Key_Less,
        ".": Qt.Key_Period,
        ">": Qt.Key_Greater,
        "/": Qt.Key_Slash,
        "?": Qt.Key_Question,
        # Numpad Keys
        "Num0": Qt.Key_0,
        "Num1": Qt.Key_1,
        "Num2": Qt.Key_2,
        "Num3": Qt.Key_3,
        "Num4": Qt.Key_4,
        "Num5": Qt.Key_5,
        "Num6": Qt.Key_6,
        "Num7": Qt.Key_7,
        "Num8": Qt.Key_8,
        "Num9": Qt.Key_9,
        "Num+": Qt.Key_Plus,
        "Num-": Qt.Key_Minus,
        "Num*": Qt.Key_Asterisk,
        "Num/": Qt.Key_Slash,
        "NumEnter": Qt.Key_Enter,
        "NumLock": Qt.Key_NumLock,
        "NumDecimal": Qt.Key_Period,
    }

    # Mapping of modifier strings to Qt.KeyboardModifier flags
    MODIFIER_MAP = {
        "Ctrl": Qt.ControlModifier,
        "Control": Qt.ControlModifier,
        "Shift": Qt.ShiftModifier,
        "Alt": Qt.AltModifier,
        "Meta": Qt.MetaModifier,
    }

    @classmethod
    def pressed(cls, key_event: QKeyEvent, key_str: str) -> bool:
        """Check if the pressed key matches the given string.

        Args:
            key_event (QKeyEvent): The key event from keyPressEvent.
            key_str (str): The key to check (e.g., "A", "Enter", "Ctrl+Shift+A").

        Returns:
            bool: True if the pressed key matches, False otherwise.

        Raises:
            ValueError: If the key_str is invalid or not mapped.
        """
        if "+" in key_str:
            # Handle modifier combinations (e.g., "Ctrl+A")
            parts = [part.strip() for part in key_str.split("+")]
            modifiers_ok = True

            # Check all parts except last as modifiers
            for mod_str in parts[:-1]:
                qt_mod = cls.MODIFIER_MAP.get(mod_str)
                if qt_mod is None:
                    raise ValueError(f"Invalid modifier: {mod_str}")
                if not (key_event.modifiers() & qt_mod):
                    modifiers_ok = False

            # Check the main key (last part)
            qt_key = cls.KEY_MAP.get(parts[-1])
            if qt_key is None:
                raise ValueError(f"Key '{parts[-1]}' is not mapped in KEY_MAP.")

            return modifiers_ok and (key_event.key() == qt_key)

        else:
            # Single key check (e.g., "A", "Enter")
            qt_key = cls.KEY_MAP.get(key_str)
            if qt_key is None:
                raise ValueError(f"Key '{key_str}' is not mapped in KEY_MAP.")
            return key_event.key() == qt_key
