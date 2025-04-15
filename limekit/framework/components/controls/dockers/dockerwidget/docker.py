import lupa
from PySide6.QtWidgets import QDockWidget, QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from limekit.framework.core.engine.parts import EnginePart


class Docker(QDockWidget, EnginePart):
    name = "Dock"

    def __init__(self, title="Dock"):
        super().__init__(title, parent=None)

        self.parent_widget = QWidget()
        self.setWidget(self.parent_widget)

    def setProperties(self, props):
        """Set dock widget features based on provided properties.

        Args:
            props: Dictionary of properties to enable/disable features.
                Supported keys: "floatable", "movable", "closable"
                None value resets all features.
        """
        # Initialize with no features
        features = QDockWidget.DockWidgetFeature.NoDockWidgetFeatures

        if not props:
            self.setFeatures(features)
            return

        # Map property names to their corresponding feature flags
        feature_mapping = {
            "floatable": QDockWidget.DockWidgetFeature.DockWidgetFloatable,
            "movable": QDockWidget.DockWidgetFeature.DockWidgetMovable,
            "closable": QDockWidget.DockWidgetFeature.DockWidgetClosable,
        }

        # Handle None case (reset all features)
        if None in props.values():
            self.setFeatures(features)
            return

        # Apply requested features
        for prop, value in props.items():
            if value and prop in feature_mapping:
                features |= feature_mapping[prop]

        self.setFeatures(features)

    """
    we want PyQt to save and restore the dock widget’s
    size and position, and since there could be any number of dock widgets, PyQt
    uses the object name to distinguish between them
    """

    def setName(self, name):
        self.setObjectName(name)

    def setVisible(self, visible):
        super().setVisible(visible)

    def setTitleBarChild(self, child):
        self.setTitleBarWidget(child)

    """
    Represents areas permitted areas for docking; more like magnetic areas
    could have been setAreas but I thought the "magnetic" name madeit look
    cool instead.
    
    Coz whenever one tries to dock some widget onto some areas, the allowed areas
    respond with a strong magnetic pull to signal the use that the particular area
    is ready to dock.
    
        Available positional enums
    NoDockWidgetArea
    LeftDockWidgetArea
    RightDockWidgetArea
    TopDockWidgetArea
    BottomDockWidgetArea
    AllDockWidgetAreas
    DockWidgetArea_Mask
    
    Set the allowed areas for a QDockWidget based on a list of areas.
        Multiple strings can be passed to set the allowed areas accordingly.
        
        Parameters:
            areas (list): list indicating the sides where the QDockWidget is allowed to be docked.
                        Valid strings are "top", "bottom", "left", and "right".
    """

    def setMagneticAreas(self, areas):
        allowed_areas = Qt.NoDockWidgetArea

        if areas:
            for area in areas.values():
                if area == "top":
                    allowed_areas |= Qt.DockWidgetArea.TopDockWidgetArea

                if area == "bottom":
                    allowed_areas |= Qt.DockWidgetArea.BottomDockWidgetArea

                if area == "left":
                    allowed_areas |= Qt.DockWidgetArea.LeftDockWidgetArea

                if area == "right":
                    allowed_areas |= Qt.DockWidgetArea.RightDockWidgetArea

                if area == "all":
                    allowed_areas |= Qt.DockWidgetArea.AllDockWidgetAreas

                if area == None:
                    allowed_areas = Qt.NoDockWidgetArea

        self.setAllowedAreas(allowed_areas)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setIcon(self, icon):
        self.setWindowIcon(QIcon(icon))

    def setSize(self, width, height):
        self.resize(width, height)

    def setMinHeight(self, height):
        self.setMinimumHeight(height)

    def setMaxHeight(self, height):
        self.setMaximumHeight(height)

    def setMinWidth(self, width):
        self.setMinimumWidth(width)

    def setMaxWidth(self, width):
        self.setMaximumWidth(width)

    # All available dock widgets are returned and can be used in construction of MenuItems
    def getDocksForMenus(self):
        return self.toggleViewAction()

    def setLayout(self, layout):
        self.parent_widget.setLayout(layout)

    def setChild(self, child):
        self.setWidget(child)

    def setMinWidth(self, width):
        self.setMinimumWidth(width)

    def setMaxWidth(self, width):
        self.setMaximumWidth(width)

    def setMinHeight(self, height):
        self.setMinimumHeight(height)

    def setMaxHeight(self, height):
        self.setMaximumHeight(height)

    def show(self):
        super().show()
