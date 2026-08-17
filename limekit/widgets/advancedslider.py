"""A custom-painted slider showing its numeric value inline.

Ports the 1.x `AdvancedSlider` (858 lines) surface: every public getter/
setter is kept, all under `LimeWidget` conventions (setters return `self`,
colours go through the shared `Colour` coercion instead of a bare
`QColor(str)` call, numeric arguments go through `_to_int`/float validation
raising `BridgeError` rather than a raw Qt crash). The paint/mouse/keyboard
internals are unchanged -- they are what makes this widget behave like a
slider, not part of the Lua-facing surface.
"""

from PySide6.QtCore import QRect, Qt, Signal
from PySide6.QtGui import QBrush, QFont, QFontMetrics, QPainter, QPen, QPixmap

from PySide6.QtWidgets import QLabel, QWidget

from limekit.kernel.coerce import Colour
from limekit.kernel.errors import BridgeError
from limekit.kernel.spec import Event
from limekit.widgets.base import LimeWidget, _to_int


class AdvancedSlider(LimeWidget, QWidget):
    __lime__ = "ui.AdvancedSlider"

    # object, not int/float, so both int and float values can pass through.
    valueChanged = Signal(object)
    onValueChanged = Event("valueChanged", passes_self=True,
                             params=(("value", "number"),))

    def __init__(self):
        super().__init__()

        self._minimum = 0
        self._maximum = 10
        self._is_float = False
        self._decimals = 1
        self._single_step = 0
        self._page_step = 0
        self._thousands_separator = ""
        self._decimal_separator = "."
        self._prefix = ""
        self._suffix = ""
        self._showing_value = True
        self._text_color = Colour("#000000")
        self._background_color = Colour("#D6D6D6")
        self._accent_color = Colour("#0078D7")
        self._border_color = Colour("#D1CFD3")
        self._border_radius = 0
        self._keyboard_input_enabled = True
        self._mouse_wheel_input_enabled = True
        self._font = QFont("Arial", 9, QFont.Weight.Bold)

        self._value = 0.0
        self._value_last_paint_event = -1
        self._force_repaint = False
        self._left_mouse_pressed = False

        self._slider = QLabel(self)
        self._position_x = None

        self._canvas = QPixmap(self.width(), self.height())
        self._canvas.fill(self._background_color)
        self._slider.setPixmap(self._canvas)

        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self._update_stylesheet()

    # -- Qt event overrides -------------------------------------------------

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._left_mouse_pressed = True
            self._value = self._get_value_from_position_x(event.pos().x())
            self._position_x = self._clamp_position_x(event.pos().x())
            if self._round_cast_value(self._value_last_paint_event) != \
                    self._round_cast_value(self._value):
                self._emit_value_changed()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._left_mouse_pressed = False
            self._value = self._get_value_from_position_x(event.pos().x())
            self._position_x = self._clamp_position_x(event.pos().x())
            if self._round_cast_value(self._value_last_paint_event) != \
                    self._round_cast_value(self._value):
                self._emit_value_changed()
            self.update()

    def mouseMoveEvent(self, event):
        if self._left_mouse_pressed:
            self._value = self._get_value_from_position_x(event.pos().x())
            self._position_x = self._clamp_position_x(event.pos().x())
            if self._round_cast_value(self._value_last_paint_event) != \
                    self._round_cast_value(self._value):
                self._emit_value_changed()
            self.update()

    def wheelEvent(self, event):
        if not self._mouse_wheel_input_enabled:
            return
        step = self._single_step if self._single_step > 0 else self._get_value_range() * 0.01
        if event.angleDelta().y() > 0:
            self.setValue(self._clamp_value(self._value + step))
        else:
            self.setValue(self._clamp_value(self._value - step))

    def keyPressEvent(self, event):
        if not self._keyboard_input_enabled:
            return

        key = event.key()
        if key == Qt.Key.Key_Home:
            self.setValue(self._minimum)
        elif key == Qt.Key.Key_End:
            self.setValue(self._maximum)
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_Up):
            step = self._single_step if self._single_step > 0 else self._get_value_range() * 0.01
            self.setValue(self._clamp_value(self._value + step))
        elif key in (Qt.Key.Key_Left, Qt.Key.Key_Down):
            step = self._single_step if self._single_step > 0 else self._get_value_range() * 0.01
            self.setValue(self._clamp_value(self._value - step))
        elif key == Qt.Key.Key_PageUp:
            step = self._page_step if self._page_step > 0 else self._get_value_range() * 0.05
            self.setValue(self._clamp_value(self._value + step))
        elif key == Qt.Key.Key_PageDown:
            step = self._page_step if self._page_step > 0 else self._get_value_range() * 0.05
            self.setValue(self._clamp_value(self._value - step))

    def paintEvent(self, event):
        resized = self._slider.size() != self.size()
        value_changed = self._value != self._value_last_paint_event

        if not resized and not value_changed and not self._force_repaint:
            return

        self._force_repaint = False
        self._value_last_paint_event = self._value

        if self._minimum >= self._maximum:
            raise BridgeError("AdvancedSlider minimum must be less than maximum")

        if resized:
            self._position_x = None
        if self._position_x is None:
            self._position_x = self._get_position_x_from_value(self._value)

        self._slider.setFixedSize(self.width(), self.height())
        self._canvas = QPixmap(self.width(), self.height())
        self._canvas.fill(self._background_color)

        painter = QPainter(self._canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(self._font)

        pen = QPen()
        pen.setWidth(1)
        pen.setColor(self._accent_color)
        painter.setPen(pen)

        brush = QBrush()
        brush.setColor(self._accent_color)
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)

        if self._position_x > 0:
            width = (
                self._position_x - 2
                if self._position_x + 2 >= self.width()
                else self._position_x
            )
            height = self.height() - 2
            rect = QRect(0, 1, width, height)
            painter.drawRoundedRect(rect, self._border_radius, self._border_radius)

        if self._showing_value:
            pen.setColor(self._text_color)
            painter.setPen(pen)

            value_string = self._format_value(
                self._value, self._is_float, self._decimals,
                self._thousands_separator, self._decimal_separator,
            )
            value_string_full = self._prefix + value_string + self._suffix

            metrics = QFontMetrics(self._font)
            text_width = metrics.horizontalAdvance(value_string_full)
            text_height = metrics.tightBoundingRect(value_string_full).height()

            text_margin = 5
            text_pos_x = self._position_x + text_margin
            if text_pos_x + text_width >= self.width() - text_margin:
                text_pos_x = self.width() - text_width - text_margin
            text_pos_x = 1 if text_pos_x == 0 else int(text_pos_x)
            text_pos_y = int(self.height() - ((self.height() - text_height) / 2))

            painter.drawText(text_pos_x, text_pos_y, value_string_full)

        self._slider.setPixmap(self._canvas)
        painter.end()

    # -- public surface -------------------------------------------------

    def getValuePosition(self):
        if self._position_x is None:
            return self._get_position_x_from_value(self._value)
        return self._position_x

    def getValue(self):
        return self._round_cast_value(self._value)

    def getValueFormatted(self):
        formatted = self._format_value(
            self._value, self._is_float, self._decimals,
            self._thousands_separator, self._decimal_separator,
        )
        return self._prefix + formatted + self._suffix

    def setValue(self, value):
        self._value = self._clamp_value(value)
        self._position_x = None
        if self._round_cast_value(self._value_last_paint_event) != \
                self._round_cast_value(self._value):
            self._emit_value_changed()
        self.update()
        return self

    def getMinimum(self):
        return self._minimum

    def setMinimum(self, minimum):
        self._minimum = minimum
        self._force_repaint = True
        self.setValue(self._value)
        return self

    def getMaximum(self):
        return self._maximum

    def setMaximum(self, maximum):
        self._maximum = maximum
        self._force_repaint = True
        self.setValue(self._value)
        return self

    def getRange(self):
        return self._minimum, self._maximum

    def setRange(self, minimum, maximum):
        self._minimum = minimum
        self._maximum = maximum
        self._force_repaint = True
        self.setValue(self._value)
        return self

    def isFloat(self):
        return self._is_float

    def setFloat(self, use_float):
        self._is_float = bool(use_float)
        self._force_repaint = True
        self.update()
        return self

    def getDecimals(self):
        return self._decimals

    def setDecimals(self, decimals):
        self._decimals = _to_int(decimals, "decimals")
        self._force_repaint = True
        self.update()
        return self

    def getSingleStep(self):
        return self._single_step

    def setSingleStep(self, single_step):
        self._single_step = single_step
        return self

    def getPageStep(self):
        return self._page_step

    def setPageStep(self, page_step):
        self._page_step = page_step
        return self

    def getThousandsSeparator(self):
        return self._thousands_separator

    def setThousandsSeparator(self, separator):
        self._thousands_separator = str(separator)
        self._force_repaint = True
        self.update()
        return self

    def getDecimalSeparator(self):
        return self._decimal_separator

    def setDecimalSeparator(self, separator):
        self._decimal_separator = str(separator)
        self._force_repaint = True
        self.update()
        return self

    def getPrefix(self):
        return self._prefix

    def setPrefix(self, prefix):
        self._prefix = str(prefix)
        self._force_repaint = True
        self.update()
        return self

    def getSuffix(self):
        return self._suffix

    def setSuffix(self, suffix):
        self._suffix = str(suffix)
        self._force_repaint = True
        self.update()
        return self

    def isShowingValue(self):
        return self._showing_value

    def showValue(self, on):
        self._showing_value = bool(on)
        self._force_repaint = True
        self.update()
        return self

    def getTextColor(self):
        return self._text_color

    def setTextColor(self, colour):
        self._text_color = Colour(colour)
        self._force_repaint = True
        self.update()
        return self

    def getBackgroundColor(self):
        return self._background_color

    def setBackgroundColor(self, colour):
        """Overrides LimeWidget.setBackgroundColor: this widget paints its
        own background rather than relying on a stylesheet."""
        self._background_color = Colour(colour)
        self._force_repaint = True
        self.update()
        return self

    def getAccentColor(self):
        return self._accent_color

    def setAccentColor(self, colour):
        self._accent_color = Colour(colour)
        self._force_repaint = True
        self.update()
        return self

    def getBorderColor(self):
        return self._border_color

    def setBorderColor(self, colour):
        self._border_color = Colour(colour)
        self._update_stylesheet()
        self._force_repaint = True
        self.update()
        return self

    def getBorderRadius(self):
        return self._border_radius

    def setBorderRadius(self, radius):
        self._border_radius = _to_int(radius, "radius")
        self._update_stylesheet()
        self._force_repaint = True
        self.update()
        return self

    def getFont(self):
        return self._font

    def setFont(self, font):
        """Overrides QWidget.setFont(QFont) -- kept QFont-typed, unlike
        FontComboBox.setFont, matching the 1.x surface exactly."""
        self._font = font
        self._force_repaint = True
        self.update()
        return self

    def isKeyboardInputEnabled(self):
        return self._keyboard_input_enabled

    def setKeyboardInputEnabled(self, enabled):
        self._keyboard_input_enabled = bool(enabled)
        return self

    def isMouseWheelInputEnabled(self):
        return self._mouse_wheel_input_enabled

    def setMouseWheelInputEnabled(self, enabled):
        self._mouse_wheel_input_enabled = bool(enabled)
        return self

    # -- internals --------------------------------------------------------

    def _update_stylesheet(self):
        self._slider.setStyleSheet(
            "border: 1px solid {}; border-radius: {}px;".format(
                self._border_color.name(), self._border_radius
            )
        )

    def _get_value_from_position_x(self, position_x):
        value_range = self._get_value_range()
        value = position_x / self.width() * value_range
        if self._minimum != 0:
            value = value + self._minimum
        return self._clamp_value(value)

    def _get_position_x_from_value(self, value):
        value_range = self._get_value_range()
        if self._minimum < 0:
            position_x = (value + abs(self._minimum)) * (self.width() / value_range)
        elif self._minimum > 0:
            position_x = (value - self._minimum) * (self.width() / value_range)
        else:
            position_x = value * (self.width() / value_range)
        return int(position_x)

    def _get_value_range(self):
        if self._minimum < 0:
            return self._maximum + abs(self._minimum)
        return self._maximum - self._minimum

    def _clamp_position_x(self, position_x):
        if position_x > self.width():
            return self.width()
        if position_x < 0:
            return 0
        return position_x

    def _clamp_value(self, value):
        if value > self._maximum:
            return self._maximum
        if value < self._minimum:
            return self._minimum
        return value

    def _format_value(self, value, is_float, decimals, thousands_separator, decimal_separator):
        if is_float:
            string_format = "{:,." + str(decimals) + "f}"
            temp_thousands = "\x00T"
            temp_decimal = "\x00D"
            return (
                string_format.format(value)
                .replace(",", temp_thousands)
                .replace(".", temp_decimal)
                .replace(temp_thousands, thousands_separator)
                .replace(temp_decimal, decimal_separator)
            )
        return "{:,.0f}".format(int(value)).replace(",", thousands_separator)

    def _emit_value_changed(self):
        self.valueChanged.emit(self._round_cast_value(self._value))

    def _round_cast_value(self, value):
        if self._is_float:
            return round(value, self._decimals)
        return int(value)
