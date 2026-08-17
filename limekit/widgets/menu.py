"""Menus, menu items, the menu bar, and the drop-down variant.

`QMenu`/`QMenuBar` are `QWidget`s, so `Menu`/`Menubar`/`DropMenu` use
`LimeWidget` like everything else. `MenuItem` wraps `QAction`, a `QObject`
rather than a `QWidget`, so it uses `LimeAction` (see action_base.py)
instead.

1.x's `Menu`/`Menubar` each carried three half-finished, mutually
inconsistent `buildFromTemplate`/`fromTemplate` implementations for
building a menu tree from a Lua table, none of which agreed with each other
about whether "submenu" nested under `item.submenu` or `item["submenu"]`,
and a shared, never-cleared `objects = {}` *class* attribute that leaked
every named menu item across every Menu instance ever created. None of that
is reproduced here: build the tree from Lua with `addMenuItem`/`addMenu`
directly, which is what the templating code bottomed out in anyway.
"""

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QMenuBar

from limekit.kernel.coerce import Icon
from limekit.kernel.spec import Event, Prop
from limekit.widgets.action_base import LimeAction
from limekit.widgets.base import LimeWidget


class MenuItem(LimeAction, QAction):
    __lime__ = "ui.MenuItem"

    onClick = Event("triggered", passes_self=True, params=(("item", "any"),))

    def __init__(self, text=""):
        super().__init__()
        if text:
            self.setText(str(text))


class Menu(LimeWidget, QMenu):
    __lime__ = "ui.Menu"

    title = Prop(str, qt=("title", "setTitle"), coerce=str)
    icon = Prop(object, qt=("icon", "setIcon"), coerce=Icon)

    onClick = Event("triggered", passes_self=True, params=(("item", "any"),),
                    doc="Fired when any item in the menu is chosen. The handler "
                        "receives the MenuItem that was clicked.")

    def __init__(self, title=""):
        super().__init__()
        if title:
            self.setTitle(str(title))

    def addMenuItem(self, item):
        """Qt native (`addAction`) re-exposed so it chains like every
        other Limekit builder method."""
        self.addAction(item)
        return self

    def addMenu(self, menu):
        super().addMenu(menu)
        return self

    def addSeparator(self):
        super().addSeparator()
        return self


class DropMenu(Menu):
    """A drop-down menu, e.g. attached to a ToolbarButton.

    1.x kept this as a near-duplicate of Menu (own addDropMenu/addMenuItem
    aliases, its own setImage). It needed nothing Menu doesn't already
    provide, so it is a plain subclass here instead of a second copy.
    """

    __lime__ = "ui.DropMenu"


class Menubar(LimeWidget, QMenuBar):
    __lime__ = "ui.Menubar"

    def addMenuItem(self, item):
        self.addAction(item)
        return self

    def addMenu(self, menu):
        super().addMenu(menu)
        return self
