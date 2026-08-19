"""Chart widgets: Chart, ChartView, LineChart, BarChart, BarSet, AreaChart,
ValueAxis, CategoryAxis.

`PySide6.QtCharts` is an optional PySide6 add-on. Confirmed importable in
this environment (see the Phase D report), so these tests run for real
rather than being skipped -- but every test still goes through
`limekit.charts._qtcharts.HAS_QTCHARTS` rather than assuming availability,
so this file degrades cleanly (skip, not fail) on a PySide6 build that
omits Charts.
"""

import pytest

from limekit.charts._qtcharts import HAS_QTCHARTS
from limekit.kernel.bridge import convert
from limekit.kernel.errors import BridgeError

pytestmark = pytest.mark.skipif(
    not HAS_QTCHARTS,
    reason="PySide6.QtCharts is not available in this environment",
)


@pytest.fixture
def lua():
    from lupa import LuaRuntime
    runtime = LuaRuntime(unpack_returned_tuples=True)
    convert.set_runtime(runtime)
    yield runtime
    convert.set_runtime(None)


def test_chart_title_and_animation(qapp):
    from limekit.charts.chart import Chart
    chart = Chart({"title": "Sales", "animation": "series"})
    assert chart.getTitle() == "Sales"
    assert chart.setAnimation("all") is chart


def test_chart_unknown_animation_raises_bridge_error(qapp):
    from limekit.charts.chart import Chart
    chart = Chart()
    with pytest.raises(BridgeError):
        chart.setAnimation("not-a-real-animation")


def test_linechart_append_and_setdata(qapp):
    from limekit.charts.linechart import LineChart
    line = LineChart()
    assert line.append(0, 1) is line
    assert line.setData([[1, 2], [2, 4], [3, 6]]) is line
    assert line.count() == 4


def test_linechart_setdata_rejects_malformed_points(qapp):
    from limekit.charts.linechart import LineChart
    line = LineChart()
    with pytest.raises(BridgeError):
        line.setData([[1, 2, 3]])


def test_barset_and_barchart(qapp):
    from limekit.charts.barset import BarSet
    from limekit.charts.barchart import BarChart
    from limekit.charts.valueaxis import ValueAxis

    barset = BarSet("Q1")
    assert barset.append([1, 2, 3]) is barset
    assert barset.count() == 3

    series = BarChart()
    assert series.append(barset) is series

    axis = ValueAxis()
    assert series.attachAxis(axis) is series


def test_categoryaxis_append(qapp, lua):
    from limekit.charts.categoryaxis import CategoryAxis
    axis = CategoryAxis(["Jan", "Feb", "Mar"])
    assert list(axis.categories()) == ["Jan", "Feb", "Mar"]
    assert axis.append(["Apr"]) is axis
    assert list(axis.categories()) == ["Jan", "Feb", "Mar", "Apr"]


def test_areachart_wraps_a_line_series(qapp):
    from limekit.charts.linechart import LineChart
    from limekit.charts.areachart import AreaChart
    upper = LineChart()
    upper.append(0, 0)
    area = AreaChart(upper)
    assert area.setName("region") is area


def test_valueaxis_setrange(qapp):
    from limekit.charts.valueaxis import ValueAxis
    axis = ValueAxis()
    assert axis.setRange(0, 100) is axis
    assert axis.min() == 0
    assert axis.max() == 100


def test_chartview_wraps_a_chart_and_lists_themes(qapp, lua):
    from limekit.charts.chart import Chart
    from limekit.charts.chartview import ChartView

    chart = Chart({"title": "Sales"})
    view = ChartView(chart)
    assert view.setTheme("dark") is view
    themes = convert.to_py(view.getThemes())
    assert "dark" in themes and "light" in themes


def test_chartview_unknown_theme_raises_bridge_error(qapp):
    from limekit.charts.chart import Chart
    from limekit.charts.chartview import ChartView
    view = ChartView(Chart())
    with pytest.raises(BridgeError):
        view.setTheme("not-a-real-theme")


# -- the other bar arrangements ------------------------------------------

BAR_SERIES = ("BarChart", "StackedBarChart", "PercentBarChart", "HorizontalBarChart")


@pytest.mark.parametrize("name", BAR_SERIES)
def test_every_bar_arrangement_takes_sets_and_axes(qapp, name):
    """All four share QAbstractBarSeries's API, so all four must behave
    identically here -- that is the reason they can share a base class."""
    import limekit.charts.barchart as barchart
    from limekit.charts.barset import BarSet
    from limekit.charts.valueaxis import ValueAxis

    series = getattr(barchart, name)()

    barset = BarSet("Q1")
    barset.append([1, 2, 3])
    assert series.append(barset) is series
    assert len(series.barSets()) == 1

    assert series.attachAxis(ValueAxis()) is series
    assert series.setBarWidth(0.5) is series
    assert series.barWidth() == pytest.approx(0.5)


@pytest.mark.parametrize("name", BAR_SERIES)
def test_every_bar_arrangement_is_registered(qapp, name):
    from limekit.kernel import manifest
    from limekit.kernel.registry import registry

    manifest.import_all()
    assert registry.get(f"chart.{name}").__name__ == name


@pytest.mark.parametrize("name", BAR_SERIES)
def test_bar_labels(qapp, name):
    import limekit.charts.barchart as barchart

    series = getattr(barchart, name)()
    assert series.setLabelsVisible(True) is series
    assert series.isLabelsVisible()
    assert series.setLabelsFormat("@value%") is series
    assert series.labelsFormat() == "@value%"
    for position in ("center", "insideend", "insidebase", "outsideend"):
        assert series.setLabelsPosition(position) is series


def test_bar_labels_position_rejects_unknown_name(qapp):
    from limekit.charts.barchart import StackedBarChart

    with pytest.raises(BridgeError):
        StackedBarChart().setLabelsPosition("sideways-ish")


def test_the_shared_bar_base_is_not_registered(qapp):
    """_BarSeries carries the shared API but is not a chart in its own
    right, so it must not appear in the registry."""
    from limekit.kernel import manifest
    from limekit.kernel.registry import registry

    manifest.import_all()
    assert not any(path.endswith("._BarSeries") for path in registry.paths())


# -- axis attachment on the non-bar series -------------------------------

def test_line_and_area_series_attach_to_axes(qapp):
    """`attachAxis` is Qt-native, so without a wrapper Lua's colon syntax
    passes the series twice and raises -- which meant a line chart could
    never be bound to the axes its author had built, and silently drew
    against Qt's default one instead."""
    from limekit.charts.areachart import AreaChart
    from limekit.charts.linechart import LineChart
    from limekit.charts.valueaxis import ValueAxis

    upper = LineChart()
    upper.setData([[1, 1], [2, 2]])
    lower = LineChart()
    lower.setData([[1, 0], [2, 1]])

    axis = ValueAxis()
    axis.setRange(0, 10)

    assert upper.attachAxis(axis) is upper
    assert AreaChart(upper, lower).attachAxis(axis) is not None


def test_a_chart_binds_its_series_to_the_axes_it_was_given(qapp):
    """The end-to-end version: the series must report the axes back."""
    from limekit.charts.categoryaxis import CategoryAxis
    from limekit.charts.chart import Chart
    from limekit.charts.barchart import StackedBarChart
    from limekit.charts.barset import BarSet
    from limekit.charts.valueaxis import ValueAxis

    series = StackedBarChart()
    barset = BarSet("Q1")
    barset.append([1, 2, 3])
    series.append(barset)

    chart = Chart({"title": "Totals"})
    chart.addSeries(series)

    categories = CategoryAxis(["Jan", "Feb", "Mar"])
    values = ValueAxis()
    values.setRange(0, 10)
    chart.addAxis(categories, "bottom")
    chart.addAxis(values, "left")

    series.attachAxis(categories)
    series.attachAxis(values)

    assert len(series.attachedAxes()) == 2
