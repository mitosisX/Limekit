from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from typing import Optional


class QtKeyMatcher:
    """Matches QKeyEvent against string representations of keys (e.g., 'A', 'Enter', 'Ctrl+A')."""

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

    def __init__(self, key_str: str):
        """Initialize with a key string to match against.

        Args:
            key_str: String representation of key (e.g., "A", "Enter", "Ctrl+Shift+A")
        """
        self.key_str = key_str
        self._parse_key_string(key_str)

    def _parse_key_string(self, key_str: str):
        """Parse the key string into components."""
        if "+" in key_str:
            parts = [part.strip() for part in key_str.split("+")]
            self.modifiers = [self.MODIFIER_MAP[mod] for mod in parts[:-1]]
            self.key = self.KEY_MAP[parts[-1]]
        else:
            self.modifiers = []
            self.key = self.KEY_MAP[key_str]

    def matches(self, event: QKeyEvent) -> bool:
        """Check if the key event matches the specified key combination.

        Args:
            event: The QKeyEvent to check

        Returns:
            bool: True if the event matches the key combination
        """
        # Check main key
        if event.key() != self.key:
            return False

        # Check modifiers
        for modifier in self.modifiers:
            if not event.modifiers() & modifier:
                return False

        # Ensure no extra modifiers are pressed (unless Shift is allowed for letters)
        allowed_modifiers = Qt.KeyboardModifiers()
        for mod in self.modifiers:
            allowed_modifiers |= mod

        # Allow Shift modifier for letter keys if not explicitly specified
        if (
            self.key >= Qt.Key_A and self.key <= Qt.Key_Z
        ) and Qt.ShiftModifier not in self.modifiers:
            allowed_modifiers |= Qt.ShiftModifier

        return event.modifiers() == allowed_modifiers

    @classmethod
    def is_key(cls, event: QKeyEvent, key_str: str) -> bool:
        """Convenience method to check a key event against a key string.

        Args:
            event: The QKeyEvent to check
            key_str: String representation of key (e.g., "A", "Enter", "Ctrl+Shift+A")

        Returns:
            bool: True if the event matches the key combination
        """
        return cls(key_str).matches(event)
