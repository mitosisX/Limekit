"""Every 1.x module the engine loads by name in a frozen app.

The 1.x engine finds its EngineParts by importing these at runtime, by
name, so PyInstaller's import analysis never sees them -- or anything they
import. The build adds this list to its hidden imports (see
limekit/build/constants.py); before it did, a built 1.x app started with
"Failed to import limekit.utils.sysutil: No module named 'psutil'".

Kept in its own module so the engine and the build read one list.
"""

FROZEN_MODULES = [
    # Layouts
    "limekit.components.layouts.vlayout",
    "limekit.components.layouts.hlayout",
    "limekit.components.layouts.grid",
    "limekit.components.layouts.formlayout",
    "limekit.components.layouts.stackedlayout",
    # Widgets
    "limekit.components.widgets.button",
    "limekit.components.widgets.label",
    "limekit.components.widgets.lineedit",
    "limekit.components.widgets.textfield",
    "limekit.components.widgets.checkbox",
    "limekit.components.widgets.radiobutton",
    "limekit.components.widgets.combobox",
    "limekit.components.widgets.listbox",
    "limekit.components.widgets.slider",
    "limekit.components.widgets.progressbar",
    "limekit.components.widgets.spinner",
    "limekit.components.widgets.doublespinner",
    "limekit.components.widgets.table",
    "limekit.components.widgets.treewidget",
    "limekit.components.widgets.tree_widget",
    "limekit.components.widgets.groupbox",
    "limekit.components.widgets.splitter",
    "limekit.components.widgets.spacer",
    "limekit.components.widgets.separator",
    "limekit.components.widgets.image",
    "limekit.components.widgets.gifplayer",
    "limekit.components.widgets.window",
    "limekit.components.widgets.container",
    "limekit.components.widgets.scroller",
    "limekit.components.widgets.buttongroup",
    "limekit.components.widgets.commandbutton",
    "limekit.components.widgets.lcdnumber",
    "limekit.components.widgets.font_combobox",
    "limekit.components.widgets.accordion",
    "limekit.components.widgets.knob",
    "limekit.components.widgets.advanced_slider",
    "limekit.components.widgets.horizontal_line",
    "limekit.components.widgets.vertical_line",
    "limekit.components.widgets.slidingstackedwidget",
    # Container widgets
    "limekit.components.widgets.containers.tab",
    "limekit.components.widgets.containers.tabbar",
    "limekit.components.widgets.containers.tabitem",
    # Picker widgets
    "limekit.components.widgets.pickers.calendar",
    "limekit.components.widgets.pickers.datepicker",
    "limekit.components.widgets.pickers.timepicker",
    # Item widgets
    "limekit.components.widgets.items.tableitem",
    "limekit.components.widgets.items.treeview_item",
    # Menu
    "limekit.components.menu.menu",
    "limekit.components.menu.menuitem",
    "limekit.components.menu.dropmenu",
    "limekit.components.menubar.menubar",
    # Toolbar
    "limekit.components.toolbar.toolbar",
    "limekit.components.toolbar.toolbar_button",
    # Statusbar
    "limekit.components.statusbar.statusbar",
    # Dialogs
    "limekit.components.dialogs.modal",
    "limekit.components.dialogs.messagebox",
    "limekit.components.dialogs.openfile",
    "limekit.components.dialogs.savefile",
    "limekit.components.dialogs.folderpicker",
    "limekit.components.dialogs.font",
    "limekit.components.dialogs.color",
    "limekit.components.dialogs.error",
    "limekit.components.dialogs.print_preview",
    "limekit.components.dialogs.popups.alert_dialog",
    "limekit.components.dialogs.popups.about_popup",
    "limekit.components.dialogs.popups.critical_popup",
    "limekit.components.dialogs.popups.information_popup",
    "limekit.components.dialogs.popups.warning_popup",
    "limekit.components.dialogs.popups.question_popup",
    "limekit.components.dialogs.inputs.text_dialog",
    "limekit.components.dialogs.inputs.multiline_input",
    "limekit.components.dialogs.inputs.combobox_dialog",
    "limekit.components.dialogs.inputs.integer_input",
    "limekit.components.dialogs.inputs.double_input",
    # Dockable
    "limekit.components.dockable.dockable_widget",
    # Charts
    "limekit.components.charts.chart",
    "limekit.components.charts.chartview",
    "limekit.components.charts.categoryaxis",
    "limekit.components.charts.linegraph.linechart",
    "limekit.components.charts.bar.barchart",
    "limekit.components.charts.bar.barset",
    "limekit.components.charts.area.areachart",
    "limekit.components.charts.axis.valueaxis",
    # Core utilities
    "limekit.core.paths",
    "limekit.core.clipboard",
    "limekit.core.timer",
    "limekit.core.systemtray",
    "limekit.core.system_notifcation",
    "limekit.core.database.sqlite3",
    "limekit.core.bootstrap.subprocess_runner",
    "limekit.core.bootstrap.engine_launcher",
    # Utils
    "limekit.utils.path",
    "limekit.utils.file",
    "limekit.utils.sound",
    "limekit.utils.encoding",
    "limekit.utils.fileutils",
    "limekit.utils.sysutil",
    "limekit.utils.converters",
    "limekit.utils.validators",
    "limekit.utils.emoji_str",
    "limekit.utils.utils",
    "limekit.utils.sorter",
    # GUI utilities
    "limekit.gui.app_styles",
    "limekit.gui.font",
    "limekit.gui.keyboard",
    "limekit.gui.keyboard_shortcut",
    "limekit.gui.dropshadow",
    "limekit.gui.syntax_highlighter",
    "limekit.gui.threading",
    # Theming
    "limekit.core.theming.themes.themer",
    "limekit.core.theming.themes.material.theme",
    "limekit.core.theming.themes.darkstylesheet.theme",
    "limekit.core.theming.themes.darklight.theme",
    "limekit.core.theming.themes.qtthemes.theme",
    "limekit.core.theming.themes.misc.theme",
    "limekit.core.theming.palletes.palleting",

]
