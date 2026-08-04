"""Timer, SysTray, SysNotification, DropShadow, AutoComplete.

The five small classes that closed the last gap in the 2.0 API surface --
see .superpowers/gap-report.md. Mirrors the conventions in
test_tier3_widgets.py: the `qapp` fixture comes from tests/conftest.py, the
`sink` fixture (captures guarded errors instead of printing them) is
redeclared here identically per those files' own convention.

SysTray and SysNotification wrap QSystemTrayIcon, which may not fully work
headless (no tray daemon under `QT_QPA_PLATFORM=offscreen`); those specific
behaviours are marked `skipif` with a stated reason rather than deleted, but
construction is asserted unconditionally since that's what the demos need.
"""

import pytest

from limekit.kernel.bridge.guard import reset_error_sink, set_error_sink
from limekit.kernel.errors import BridgeError


@pytest.fixture(autouse=True)
def sink():
    captured = []
    set_error_sink(captured.append)
    yield captured
    reset_error_sink()


def _no_tray():
    from PySide6.QtWidgets import QApplication, QSystemTrayIcon
    QApplication.instance() or QApplication([])
    return not QSystemTrayIcon.isSystemTrayAvailable()


_no_tray_reason = (
    "QSystemTrayIcon.isSystemTrayAvailable() is False under "
    "QT_QPA_PLATFORM=offscreen (no tray daemon in CI); construction is "
    "still asserted below since that's what the demos actually need."
)


# -- Timer ----------------------------------------------------------------

def test_timer_interval_round_trips_in_milliseconds(qapp):
    """1.x's `setInterval` passed straight through to `QTimer.setInterval`,
    which is milliseconds. Keeping that unit means a 1.x demo doing
    `Timer():setInterval(1000):start()` for a one-second tick keeps
    ticking once a second unchanged, not once a millisecond."""
    from limekit.services.timer import Timer
    timer = Timer()
    assert timer.setInterval(1000) is timer
    assert timer.getInterval() == 1000


def test_timer_single_shot_prop_round_trips(qapp):
    from limekit.services.timer import Timer
    timer = Timer()
    assert timer.setSingleShot(True) is timer
    assert timer.isSingleShot() is True
    assert timer.getSingleShot() is True


def test_timer_start_stop_and_is_active(qapp):
    from limekit.services.timer import Timer
    timer = Timer()
    timer.setInterval(10000)
    assert timer.isActive() is False
    assert timer.start() is timer
    assert timer.isActive() is True
    assert timer.stop() is timer
    assert timer.isActive() is False


def test_timer_ontimeout_fires(qapp):
    from limekit.services.timer import Timer
    timer = Timer()
    seen = []
    assert timer.setOnTimeout(lambda self: seen.append(self)) is timer
    timer.timeout.emit()
    assert seen == [timer]


def test_timer_ontimeout_is_guarded(qapp, sink):
    from limekit.services.timer import Timer
    timer = Timer()
    timer.setOnTimeout(lambda self: 1 / 0)
    timer.timeout.emit()
    assert len(sink) == 1


def test_timer_singleshot_static_invokes_callback(qapp):
    from limekit.services.timer import Timer
    seen = []
    Timer.singleShot(0, lambda: seen.append(1))
    qapp.processEvents()
    import time
    time.sleep(0.05)
    qapp.processEvents()
    assert seen == [1]


# -- SysTray ----------------------------------------------------------------

def test_systray_constructs(qapp):
    from limekit.services.systray import SysTray
    tray = SysTray()
    assert tray is not None


def test_systray_prop_round_trips(qapp):
    from limekit.services.systray import SysTray
    tray = SysTray()
    assert tray.setToolTip("hello") is tray
    assert tray.getToolTip() == "hello"
    assert tray.setVisible(True) is tray
    assert tray.getVisible() is True


def test_systray_show_hide_native_reexposed(qapp):
    from limekit.services.systray import SysTray
    tray = SysTray()
    assert tray.show() is tray
    assert tray.hide() is tray


@pytest.mark.skipif(_no_tray(), reason=_no_tray_reason)
def test_systray_onactivated_guarded(qapp, sink):
    from limekit.services.systray import SysTray
    tray = SysTray()
    tray.setOnActivated(lambda self, reason: 1 / 0)
    tray.activated.emit(SysTray.ActivationReason.Trigger)
    assert len(sink) == 1


# -- SysNotification ----------------------------------------------------------

def test_sysnotification_constructs(qapp):
    from limekit.services.sysnotification import SysNotification
    notification = SysNotification()
    assert notification is not None


def test_sysnotification_icon_prop_round_trips(qapp):
    from PySide6.QtGui import QIcon
    from limekit.services.sysnotification import SysNotification
    notification = SysNotification()
    icon = QIcon()
    assert notification.setIcon(icon) is notification
    assert notification.getIcon() is not None


def test_sysnotification_onclick_is_guarded(qapp, sink):
    from limekit.services.sysnotification import SysNotification
    notification = SysNotification()
    notification.setOnClick(lambda self: 1 / 0)
    notification.messageClicked.emit()
    assert len(sink) == 1


def test_sysnotification_unknown_icon_raises_bridgeerror(qapp):
    from limekit.services.sysnotification import SysNotification
    notification = SysNotification()
    with pytest.raises(BridgeError):
        notification.showMessage("t", "m", icon="not-a-real-icon")


@pytest.mark.skipif(_no_tray(), reason=_no_tray_reason)
def test_sysnotification_showmessage_returns_self(qapp):
    from limekit.services.sysnotification import SysNotification
    notification = SysNotification()
    assert notification.showMessage("Title", "Body") is notification


# -- DropShadow ---------------------------------------------------------------

def test_dropshadow_constructs_and_applies_to_a_widget(qapp):
    from PySide6.QtWidgets import QWidget
    from limekit.services.dropshadow import DropShadow
    widget = QWidget()
    shadow = DropShadow(widget)
    assert widget.graphicsEffect() is shadow


def test_dropshadow_defaults_match_1x(qapp):
    from limekit.services.dropshadow import DropShadow
    shadow = DropShadow()
    assert shadow.getBlurRadius() == 50
    assert shadow.getOffsetX() == 2
    assert shadow.getOffsetY() == 5
    assert shadow.getColor().name() == "#7090b0"


def test_dropshadow_prop_round_trips(qapp):
    from limekit.services.dropshadow import DropShadow
    shadow = DropShadow()
    assert shadow.setBlurRadius(10) is shadow
    assert shadow.getBlurRadius() == 10
    assert shadow.setColor("#ff0000") is shadow
    assert shadow.getColor().name() == "#ff0000"


def test_dropshadow_setoffset_round_trips(qapp):
    from limekit.services.dropshadow import DropShadow
    shadow = DropShadow()
    assert shadow.setOffset(7, 9) is shadow
    assert shadow.getOffsetX() == 7
    assert shadow.getOffsetY() == 9


def test_dropshadow_applyto_reattaches_to_a_different_widget(qapp):
    from PySide6.QtWidgets import QWidget
    from limekit.services.dropshadow import DropShadow
    first, second = QWidget(), QWidget()
    shadow = DropShadow(first)
    assert shadow.applyTo(second) is shadow
    assert second.graphicsEffect() is shadow


def test_dropshadow_blurradius_rejects_non_numeric(qapp):
    from limekit.services.dropshadow import DropShadow
    shadow = DropShadow()
    with pytest.raises(BridgeError):
        shadow.setBlurRadius("not-a-number")


# -- AutoComplete ---------------------------------------------------------------

def test_autocomplete_constructs_from_a_list(qapp):
    from limekit.services.autocomplete import AutoComplete
    completer = AutoComplete(["alpha", "beta", "gamma"])
    assert completer is not None
    assert completer.completionMode() == completer.CompletionMode.PopupCompletion


def test_autocomplete_constructs_from_a_lua_style_table(qapp):
    """Lua callers pass a table; as_sequence() accepts a plain dict of
    1-based keys the way lupa hands one back."""
    from limekit.services.autocomplete import AutoComplete
    completer = AutoComplete({1: "alpha", 2: "beta"})
    assert completer is not None


def test_autocomplete_case_sensitivity_round_trips(qapp):
    from limekit.services.autocomplete import AutoComplete
    completer = AutoComplete(["alpha"])
    assert completer.isCaseSensitive() is False
    assert completer.setCaseSensitive(True) is completer
    assert completer.isCaseSensitive() is True


def test_autocomplete_attaches_to_a_lineedit(qapp):
    from limekit.services.autocomplete import AutoComplete
    from limekit.widgets.lineedit import LineEdit
    completer = AutoComplete(["alpha", "beta"])
    field = LineEdit()
    assert field.setAutoComplete(completer) is field


# -- Dockable / ChartCanvas aliases ---------------------------------------------

def test_dockable_is_an_alias_for_dock(qapp):
    from limekit.kernel.registry import registry
    from limekit.widgets.dock import Dock
    assert registry.get("ui.Dockable") is Dock
    assert registry.get("ui.Dock") is Dock


def test_chartcanvas_is_an_alias_for_chartview(qapp):
    from limekit.kernel.registry import registry
    from limekit.charts.chartview import ChartView
    assert registry.get("chart.ChartCanvas") is ChartView
    assert registry.get("chart.ChartView") is ChartView
